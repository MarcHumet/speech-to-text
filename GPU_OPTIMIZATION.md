# GPU Usage Optimization Guide

The 12-13% GPU usage (278MiB VRAM) you're seeing is **normal behavior** for faster-whisper with GPU acceleration. Here are several ways to optimize it:

## Option 1: Lazy Model Loading (Recommended)
Modify the engine to load/unload the model on demand:

```python
# Add to FasterWhisperEngine class
def unload_model(self):
    """Unload model to free GPU memory."""
    if self.model is not None:
        del self.model
        self.model = None
        self.ready = False
        # Force garbage collection to free GPU memory
        import gc
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except ImportError:
            pass
        logger.info("🗑️ Faster Whisper model unloaded from GPU")
```

## Option 2: Use Smaller Model
Switch to a lighter model in your config:

```yaml
model:
  type: faster-whisper
  path: tiny  # Uses ~40MB instead of ~280MB
  # Options: tiny (~40MB), base (~280MB), small (~960MB)
```

## Option 3: CPU-Only Mode
Force CPU usage to eliminate GPU usage:

```yaml
model:
  type: whisper  # Uses regular whisper (CPU-only)
  path: base
```

## Option 4: On-Demand Service
Run service only when needed instead of continuously.

## Option 5: Model Memory Management
Configure faster-whisper with memory-efficient settings.

## Current Memory Usage Breakdown:
- Base model: ~280MB VRAM (what you're seeing)
- Tiny model: ~40MB VRAM (7x less)
- CPU-only: 0MB VRAM, uses RAM instead

## Recommendation:
Try Option 1 (lazy loading) + Option 2 (tiny model) for best balance of performance and memory usage.