#!/usr/bin/env python3
"""
Performance comparison script: Native vs Podman containerized STT service
"""
import subprocess
import time
import json
import psutil
import os
import sys
from datetime import datetime

def get_gpu_stats():
    """Get current GPU memory and utilization stats."""
    try:
        result = subprocess.run([
            'nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            return {
                'memory_used': int(parts[0]),
                'memory_total': int(parts[1]),
                'gpu_util': int(parts[2])
            }
    except Exception as e:
        print(f"Error getting GPU stats: {e}")
    return None

def measure_startup_time(command, name):
    """Measure service startup time."""
    print(f"\n🚀 Testing {name} startup time...")
    
    # Get baseline stats
    baseline_gpu = get_gpu_stats()
    baseline_mem = psutil.virtual_memory().used / 1024 / 1024  # MB
    
    start_time = time.time()
    
    # Start service
    process = subprocess.Popen(
        command, shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for service to be ready (look for "Service running" message)
    startup_complete = False
    while not startup_complete and process.poll() is None:
        if process.stdout and process.stdout.readable():
            line = process.stdout.readline()
            if "Service running" in line or "STT Service started successfully" in line:
                startup_complete = True
                break
        time.sleep(0.1)
    
    startup_time = time.time() - start_time
    
    # Give it a moment to fully initialize
    time.sleep(2)
    
    # Get post-startup stats
    post_gpu = get_gpu_stats()
    post_mem = psutil.virtual_memory().used / 1024 / 1024  # MB
    
    # Calculate resource usage
    gpu_memory_increase = (post_gpu['memory_used'] - baseline_gpu['memory_used']) if post_gpu and baseline_gpu else 0
    ram_increase = post_mem - baseline_mem
    
    results = {
        'startup_time': round(startup_time, 2),
        'gpu_memory_used': gpu_memory_increase,
        'ram_used': round(ram_increase, 1),
        'gpu_utilization': post_gpu['gpu_util'] if post_gpu else 0,
        'process': process
    }
    
    print(f"✅ {name} started in {startup_time:.2f}s")
    print(f"   GPU Memory: +{gpu_memory_increase}MB")
    print(f"   RAM: +{ram_increase:.1f}MB") 
    print(f"   GPU Util: {results['gpu_utilization']}%")
    
    return results

def simulate_transcription_load(name, duration=10):
    """Simulate transcription workload and measure performance."""
    print(f"\n🎯 Testing {name} transcription performance...")
    
    # Measure resource usage during operation
    start_time = time.time()
    gpu_utils = []
    
    while time.time() - start_time < duration:
        gpu_stats = get_gpu_stats()
        if gpu_stats:
            gpu_utils.append(gpu_stats['gpu_util'])
        time.sleep(0.5)
    
    avg_gpu_util = sum(gpu_utils) / len(gpu_utils) if gpu_utils else 0
    
    print(f"   Average GPU utilization: {avg_gpu_util:.1f}%")
    return {'avg_gpu_util': round(avg_gpu_util, 1)}

def cleanup_service(process, name):
    """Clean up running service."""
    print(f"\n🧹 Stopping {name}...")
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    
    # Extra cleanup for containers
    if "podman" in name.lower():
        subprocess.run(["podman-compose", "down"], capture_output=True, timeout=10)
    
    time.sleep(3)  # Allow resources to free up

def main():
    """Main performance comparison."""
    print("🔬 STT Service Performance Comparison: Native vs Podman")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Native execution
    try:
        native_cmd = "cd /home/marc/project/speech-to-text && uv run python cli.py run"
        native_results = measure_startup_time(native_cmd, "Native Python")
        
        # Test performance under load
        native_perf = simulate_transcription_load("Native Python")
        native_results.update(native_perf)
        
        results['native'] = native_results
        
        # Cleanup
        cleanup_service(native_results['process'], "Native Python")
        
    except Exception as e:
        print(f"❌ Native test failed: {e}")
        results['native'] = {'error': str(e)}
    
    # Test 2: Podman containerized
    try:
        # Check if podman-compose is available
        check_podman = subprocess.run(["which", "podman-compose"], capture_output=True)
        if check_podman.returncode != 0:
            print("⚠️ podman-compose not found, skipping container test")
            results['podman'] = {'error': 'podman-compose not available'}
        else:
            podman_cmd = "cd /home/marc/project/speech-to-text && podman-compose up"
            podman_results = measure_startup_time(podman_cmd, "Podman Container")
            
            # Test performance under load  
            podman_perf = simulate_transcription_load("Podman Container")
            podman_results.update(podman_perf)
            
            results['podman'] = podman_results
            
            # Cleanup
            cleanup_service(podman_results['process'], "Podman Container")
            
    except Exception as e:
        print(f"❌ Podman test failed: {e}")
        results['podman'] = {'error': str(e)}
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE COMPARISON SUMMARY")
    print("=" * 60)
    
    if 'native' in results and 'error' not in results['native']:
        print(f"🐍 NATIVE:")
        print(f"   Startup Time: {results['native']['startup_time']}s")
        print(f"   GPU Memory: {results['native']['gpu_memory_used']}MB")
        print(f"   RAM Usage: {results['native']['ram_used']}MB")
        print(f"   Avg GPU Util: {results['native']['avg_gpu_util']}%")
    
    if 'podman' in results and 'error' not in results['podman']:
        print(f"\n🐳 PODMAN:")
        print(f"   Startup Time: {results['podman']['startup_time']}s")
        print(f"   GPU Memory: {results['podman']['gpu_memory_used']}MB")  
        print(f"   RAM Usage: {results['podman']['ram_used']}MB")
        print(f"   Avg GPU Util: {results['podman']['avg_gpu_util']}%")
        
        # Calculate differences
        if 'native' in results and 'error' not in results['native']:
            startup_diff = results['podman']['startup_time'] - results['native']['startup_time']
            ram_diff = results['podman']['ram_used'] - results['native']['ram_used']
            
            print(f"\n📈 DIFFERENCE (Container vs Native):")
            print(f"   Startup Time: {startup_diff:+.2f}s ({startup_diff/results['native']['startup_time']*100:+.1f}%)")
            print(f"   RAM Overhead: {ram_diff:+.1f}MB ({ram_diff/results['native']['ram_used']*100:+.1f}%)")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'performance_results_{timestamp}.json', 'w') as f:
        # Remove process objects for JSON serialization
        clean_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                clean_results[key] = {k: v for k, v in value.items() if k != 'process'}
            else:
                clean_results[key] = value
        
        json.dump(clean_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: performance_results_{timestamp}.json")

if __name__ == "__main__":
    main()