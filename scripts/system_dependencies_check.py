import subprocess
import sys

print('Testing system dependencies...')

def test_import(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError as e:
        print(f'❌ {module_name}: {e}')
        return False
    except Exception as e:
        print(f'⚠️  {module_name}: {e}')
        return True

# Test critical imports
modules = {
    'sounddevice': 'Audio capture (needs PortAudio)',
    'pyautogui': 'Keyboard automation (needs X11 libs)',
    'pynput': 'Input capture (needs X11 libs)',  
    'keyboard': 'Hotkey detection',
    'whisper': 'Speech-to-text engine'
}
def test_dependencies():
    print("\n" + "="*60)
    print("Testing System Dependencies")
    print("="*60)
    for module, description in modules.items():
        if test_import(module):
            print(f'✅ {module} - {description}')

if __name__ == "__main__":
    test_dependencies()
