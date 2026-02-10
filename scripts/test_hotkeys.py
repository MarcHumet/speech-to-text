from pynput.keyboard import GlobalHotKeys
import time

# from cli import test_keyboard

def detected():
    print('✅ HOTKEY WORKS!')

def test_hotkeys():
    hotkeys = GlobalHotKeys({'<ctrl>+<shift>+<space>': detected})
    hotkeys.start()
    print('Press Ctrl+Shift+Space...')
    time.sleep(10)
    hotkeys.stop()


if __name__ == '__main__':
    test_hotkeys()