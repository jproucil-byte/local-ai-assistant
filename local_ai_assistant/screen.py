"""Capture one frame on request or during an explicitly started screen watch."""
from io import BytesIO

def capture_primary_screen() -> bytes:
    import mss
    from PIL import Image
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[1])
        image = Image.frombytes('RGB', shot.size, shot.rgb)
    image.thumbnail((1600, 1000))
    out = BytesIO()
    image.save(out, format='PNG')
    return out.getvalue()
