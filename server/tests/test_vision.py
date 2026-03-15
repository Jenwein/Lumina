import pytest
from PIL import Image
from lumina.vision.coordinates import CoordinateConverter, RatioPoint, ScreenPoint
from lumina.vision.window_info import WindowRect
import os

def test_coordinate_converter():
    rect = WindowRect(x=100, y=200, width=1000, height=800)
    
    # Ratio to Screen
    rp = RatioPoint(0.5, 0.5)
    sp = CoordinateConverter.ratio_to_screen(rp, rect)
    assert sp.x == 600  # 100 + 0.5 * 1000
    assert sp.y == 600  # 200 + 0.5 * 800
    
    # Screen to Ratio
    sp2 = ScreenPoint(600, 600)
    rp2 = CoordinateConverter.screen_to_ratio(sp2, rect)
    assert rp2.rx == 0.5
    assert rp2.ry == 0.5
    
    # Boundary tests
    assert CoordinateConverter.ratio_to_screen(RatioPoint(0, 0), rect) == ScreenPoint(100, 200)
    assert CoordinateConverter.ratio_to_screen(RatioPoint(1, 1), rect) == ScreenPoint(1100, 1000)

def test_bbox_to_ratio_center():
    rp = CoordinateConverter.bbox_to_ratio_center(100, 100, 200, 100, 1000, 1000)
    # Center is (100+100, 100+50) = (200, 150)
    # Ratio: (0.2, 0.15)
    assert rp.rx == 0.2
    assert rp.ry == 0.15

@pytest.mark.skipif(os.name != 'nt', reason="Windows specific")
def test_window_manager_basics():
    from lumina.vision.window_info import WindowManager
    wm = WindowManager()
    fg = wm.get_foreground_window()
    assert fg is not None
    assert fg.hwnd != 0
    assert fg.rect.width > 0
