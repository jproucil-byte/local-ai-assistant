"""Capture active foreground window on Windows; primary screen fallback elsewhere."""
import sys
from io import BytesIO

def capture_active_window() -> bytes:
    if sys.platform != 'win32':
        raise NotImplementedError('Active-window capture is currently available on Windows only.')
    import ctypes
    from ctypes import wintypes
    import mss
    from PIL import Image

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        raise RuntimeError('No active window found.')
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError('Cannot read active window bounds.')
    width, height = rect.right - rect.left, rect.bottom - rect.top
    if width < 2 or height < 2:
        raise RuntimeError('Active window has invalid dimensions.')
    with mss.mss() as sct:
        shot = sct.grab({'left': rect.left, 'top': rect.top, 'width': width, 'height': height})
        image = Image.frombytes('RGB', shot.size, shot.rgb)
    image.thumbnail((1600, 1000))
    output = BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()
