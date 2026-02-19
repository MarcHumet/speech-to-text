#!/usr/bin/env python3
"""Test Catalan STT model with audio file."""

import sys
import time
import threading
import numpy as np
import soundfile as sf
import psutil
from pathlib import Path

# Add parent directory to path to import stt_service
sys.path.insert(0, str(Path(__file__).parent.parent))

from stt_service.core.engine import FasterWhisperEngine
from stt_service.core.logger import get_logger

logger = get_logger(__name__)


class ResourceMonitor:
    """Monitor CPU/RAM and GPU usage during execution."""
    
    def __init__(self, interval=0.1):
        """Initialize resource monitor.
        
        Args:
            interval: Monitoring interval in seconds
        """
        self.interval = interval
        self.monitoring = False
        self.thread = None
        
        # Resource usage tracking
        self.max_ram_mb = 0
        self.max_ram_percent = 0
        self.max_gpu_mem_mb = 0
        self.max_gpu_util = 0
        self.gpu_available = False
        
        # Try to initialize NVIDIA GPU monitoring
        try:
            import pynvml
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.gpu_available = True
            self.pynvml = pynvml
            logger.info("GPU monitoring initialized")
        except Exception as e:
            logger.warning(f"GPU monitoring not available: {e}")
            self.pynvml = None
    
    def _monitor(self):
        """Monitor resources in background thread."""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                # Monitor RAM
                mem_info = process.memory_info()
                ram_mb = mem_info.rss / (1024 * 1024)
                ram_percent = process.memory_percent()
                
                self.max_ram_mb = max(self.max_ram_mb, ram_mb)
                self.max_ram_percent = max(self.max_ram_percent, ram_percent)
                
                # Monitor GPU if available
                if self.gpu_available and self.pynvml:
                    try:
                        mem_info = self.pynvml.nvmlDeviceGetMemoryInfo(self.handle)
                        util_info = self.pynvml.nvmlDeviceGetUtilizationRates(self.handle)
                        
                        gpu_mem_mb = mem_info.used / (1024 * 1024)
                        gpu_util = util_info.gpu
                        
                        self.max_gpu_mem_mb = max(self.max_gpu_mem_mb, gpu_mem_mb)
                        self.max_gpu_util = max(self.max_gpu_util, gpu_util)
                    except Exception as e:
                        logger.debug(f"GPU monitoring error: {e}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                break
    
    def start(self):
        """Start monitoring resources."""
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop monitoring and return results."""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        return {
            'ram_mb': self.max_ram_mb,
            'ram_percent': self.max_ram_percent,
            'gpu_mem_mb': self.max_gpu_mem_mb,
            'gpu_util': self.max_gpu_util,
            'gpu_available': self.gpu_available
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def load_audio(audio_path: str, target_sr: int = 16000) -> np.ndarray:
    """Load audio file and resample if needed.
    
    Args:
        audio_path: Path to audio file
        target_sr: Target sample rate (default 16000 for Whisper)
        
    Returns:
        Audio data as float32 numpy array
    """
    try:
        # Load audio file
        audio, sr = sf.read(audio_path, dtype='float32')
        logger.info(f"Loaded audio: {audio_path}")
        logger.info(f"Original sample rate: {sr} Hz, shape: {audio.shape}")
        
        # Convert stereo to mono if needed
        if len(audio.shape) == 2:
            audio = np.mean(audio, axis=1)
            logger.info("Converted stereo to mono")
        
        # Resample if needed (simple resampling, for better quality use librosa)
        if sr != target_sr:
            logger.warning(f"Audio sample rate ({sr}) differs from target ({target_sr})")
            logger.info("Consider using librosa for better resampling quality")
            # Simple resampling (not high quality, but works)
            from scipy import signal
            num_samples = int(len(audio) * target_sr / sr)
            audio = signal.resample(audio, num_samples)
            logger.info(f"Resampled to {target_sr} Hz")
        
        return audio.astype(np.float32)
        
    except Exception as e:
        logger.error(f"Failed to load audio: {e}")
        raise


def test_catalan_transcription(audio_path: str):
    """Test Catalan STT transcription.
    
    Args:
        audio_path: Path to audio WAV file
    """
    print("=" * 80)
    print("🎤 Testing Catalan STT Model (ProjecteAINA)")
    print("=" * 80)
    
    # Check if audio file exists
    if not Path(audio_path).exists():
        print(f"❌ Error: Audio file not found: {audio_path}")
        return
    
    try:
        # Load audio
        print(f"\n📂 Loading audio: {audio_path}")
        load_start = time.time()
        audio = load_audio(audio_path)
        load_time = time.time() - load_start
        duration = len(audio) / 16000
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Shape: {audio.shape}")
        print(f"   Sample rate: 16000 Hz")
        print(f"   Load time: {load_time:.2f}s")
        
        # Initialize Catalan STT engine
        print("\n🤖 Initializing Catalan STT Engine...")
        print("   Model: projecte-aina/faster-whisper-large-v3-ca-3catparla")
        engine = FasterWhisperEngine(language='ca')
        
        # Load model (will auto-select Catalan model)
        print("\n⏳ Loading model (this may take a while on first run)...")
        model_load_start = time.time()
        engine.load_model('base')  # Model path is ignored for Catalan
        model_load_time = time.time() - model_load_start
        print(f"   Model load time: {model_load_time:.2f}s")
        
        # Check GPU
        if engine.device == 'cuda':
            print(f"   ✅ Using GPU with {engine.compute_type} compute type")
        else:
            print(f"   ℹ️  Using CPU with {engine.compute_type} compute type")
        
        # Transcribe with resource monitoring
        print("\n🎯 Transcribing...")
        print("   📊 Monitoring resources...")
        
        with ResourceMonitor(interval=0.1) as monitor:
            transcribe_start = time.time()
            text = engine.transcribe(audio, language='ca')
            transcribe_time = time.time() - transcribe_start
        
        # Get resource usage
        resources = monitor.stop()
        
        # Display results
        print("\n" + "=" * 80)
        print("📝 TRANSCRIPTION RESULT")
        print("=" * 80)
        if text:
            print(f"\n{text}\n")
        else:
            print("\n⚠️  No transcription returned (empty or silent audio?)\n")
        
        # Performance metrics
        print("=" * 80)
        print("⚡ PERFORMANCE METRICS")
        print("=" * 80)
        print(f"\n⏱️  Timing:")
        print(f"   • Audio loading:    {load_time:.2f}s")
        print(f"   • Model loading:    {model_load_time:.2f}s")
        print(f"   • Transcription:    {transcribe_time:.2f}s")
        print(f"   • Real-time factor: {transcribe_time/duration:.2f}x")
        print(f"   • Total time:       {load_time + model_load_time + transcribe_time:.2f}s")
        
        print(f"\n💾 Memory Usage:")
        print(f"   • Peak RAM:         {resources['ram_mb']:.1f} MB ({resources['ram_percent']:.1f}%)")
        
        if resources['gpu_available']:
            print(f"\n🎮 GPU Usage:")
            print(f"   • Peak VRAM:        {resources['gpu_mem_mb']:.1f} MB")
            print(f"   • Peak utilization: {resources['gpu_util']:.1f}%")
        else:
            print(f"\n🎮 GPU: Not available (CPU mode)")
        
        print("\n" + "=" * 80)
        if text:
            print(f"✅ Successfully transcribed {duration:.2f} seconds of Catalan audio")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during transcription: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Default audio path
    audio_path = "/home/marc/project/speech-to-text/scripts/test_catala.wav"
    
    # Allow custom audio path from command line
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
    
    test_catalan_transcription(audio_path)
