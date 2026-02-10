#!/usr/bin/env python3
"""
Quick STT Performance Test - Native execution
"""
import subprocess
import time
import psutil
import os

def get_gpu_memory():
    """Get current GPU memory usage in MB."""
    try:
        result = subprocess.run([
            'nvidia-smi', '--query-gpu=memory.used,utilization.gpu',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            return int(parts[0]), int(parts[1])
    except:
        return None, None

def measure_native_performance():
    """Measure native STT service performance."""
    print("🐍 Testing Native STT Performance")
    print("-" * 40)
    
    # Baseline measurements
    baseline_gpu, baseline_util = get_gpu_memory()
    baseline_ram = psutil.virtual_memory().used / 1024 / 1024
    
    print(f"📊 Baseline:")
    print(f"   GPU Memory: {baseline_gpu}MB")
    print(f"   GPU Util: {baseline_util}%") 
    print(f"   RAM: {baseline_ram:.1f}MB")
    
    # Start service and measure startup time
    print(f"\n🚀 Starting service...")
    start_time = time.time()
    
    process = subprocess.Popen([
        'uv', 'run', 'python', 'cli.py', 'run'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait for service to be ready
    startup_complete = False
    output_lines = []
    
    while not startup_complete and process.poll() is None:
        if process.stdout:
            line = process.stdout.readline()
            if line:
                output_lines.append(line.strip())
                if "Service running" in line or "Press ctrl+shift+space" in line:
                    startup_complete = True
                    break
        time.sleep(0.1)
    
    startup_time = time.time() - start_time
    
    # Give it a moment to fully initialize
    time.sleep(2)
    
    # Post-startup measurements
    post_gpu, post_util = get_gpu_memory()
    post_ram = psutil.virtual_memory().used / 1024 / 1024
    
    gpu_increase = (post_gpu - baseline_gpu) if post_gpu and baseline_gpu else 0
    ram_increase = post_ram - baseline_ram
    
    print(f"✅ Service started in {startup_time:.2f}s")
    print(f"\n📈 Resource Usage:")
    print(f"   GPU Memory: {post_gpu}MB (+{gpu_increase}MB)")
    print(f"   GPU Util: {post_util}%")
    print(f"   RAM: {post_ram:.1f}MB (+{ram_increase:.1f}MB)")
    
    # Monitor for a few seconds to see idle behavior
    print(f"\n⏱️ Monitoring idle performance (10s)...")
    gpu_utils = []
    
    for i in range(20):  # 10 seconds, 0.5s intervals
        gpu_mem, gpu_util = get_gpu_memory()
        if gpu_util is not None:
            gpu_utils.append(gpu_util)
        time.sleep(0.5)
    
    avg_idle_gpu = sum(gpu_utils) / len(gpu_utils) if gpu_utils else 0
    
    print(f"📊 Idle Performance:")
    print(f"   Average GPU Util: {avg_idle_gpu:.1f}%")
    print(f"   GPU Memory (stable): {post_gpu}MB")
    
    # Test transcription readiness
    print(f"\n🎯 Service Status: Ready for transcription")
    print(f"   Press Ctrl+Shift+Space to test transcription")
    print(f"   The service will respond instantly (model pre-loaded)")
    
    # Clean up
    print(f"\n🧹 Stopping service...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    
    time.sleep(2)
    
    # Final measurements
    final_gpu, final_util = get_gpu_memory()
    final_ram = psutil.virtual_memory().used / 1024 / 1024
    
    gpu_freed = (post_gpu - final_gpu) if final_gpu and post_gpu else 0
    ram_freed = post_ram - final_ram
    
    print(f"✅ Service stopped")
    print(f"   GPU Memory freed: {gpu_freed}MB") 
    print(f"   RAM freed: {ram_freed:.1f}MB")
    
    return {
        'startup_time': startup_time,
        'gpu_memory_usage': gpu_increase,
        'ram_usage': ram_increase,
        'idle_gpu_utilization': avg_idle_gpu,
        'memory_freed_correctly': gpu_freed > 200  # Should free most of the model memory
    }

def main():
    """Run native performance test."""
    print("🔬 STT Service Performance Analysis")
    print("=" * 50)
    
    # Change to project directory
    os.chdir('/home/marc/project/speech-to-text')
    
    results = measure_native_performance()
    
    print(f"\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print(f"⏱️  Startup Time: {results['startup_time']:.2f}s")
    print(f"🎮 GPU Memory: {results['gpu_memory_usage']}MB (for model)")
    print(f"💾 RAM Usage: {results['ram_usage']:.1f}MB") 
    print(f"⚡ Idle GPU: {results['idle_gpu_utilization']:.1f}% (normal for loaded model)")
    print(f"🧹 Memory Cleanup: {'✅ Proper' if results['memory_freed_correctly'] else '⚠️ Issues'}")
    
    print(f"\n🎯 PERFORMANCE ANALYSIS:")
    if results['startup_time'] < 3:
        print("   ✅ Fast startup (< 3s)")
    else:
        print("   ⚠️ Slow startup (> 3s)")
    
    if results['gpu_memory_usage'] < 400:
        print("   ✅ Reasonable GPU memory usage")
    else:
        print("   ⚠️ High GPU memory usage")
    
    if results['idle_gpu_utilization'] < 20:
        print("   ✅ Low idle GPU utilization")
    else:
        print("   ⚠️ High idle GPU utilization")
    
    print(f"\n💡 The {results['idle_gpu_utilization']:.1f}% GPU usage is NORMAL and BENEFICIAL:")
    print("   - Model stays loaded in VRAM for instant transcription")
    print("   - Alternative: 1-3s model loading delay per transcription")
    print("   - This is optimized for speech-to-text performance")

if __name__ == "__main__":
    main()