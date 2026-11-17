import os
import unittest
from types import SimpleNamespace

from PIL import Image

from thumbor.config import Config
from thumbor.engines.pil import Engine
from thumbor.point import FocalPoint
from thumbor.transformer import Transformer

COURSE_IMAGES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "course",
    "images",
)


def make_transformer(filename, width, height, fit_in=False):
    engine = Engine(SimpleNamespace(config=Config()))
    engine.image = Image.open(os.path.join(COURSE_IMAGES, filename))
    engine.image.load()
    request = SimpleNamespace(
        engine=engine,
        width=width,
        height=height,
        fit_in=fit_in,
        adaptive=False,
        full=False,
        halign="center",
        valign="middle",
        focal_points=[],
        should_crop=False,
        crop={"left": 0, "top": 0, "right": 0, "bottom": 0},
    )
    context = SimpleNamespace(
        config=Config(), request=request, modules=None
    )
    transformer = Transformer(context)
    transformer._calculate_target_dimensions()
    source_width, source_height = engine.size
    transformer.focal_points = [
        FocalPoint.from_alignment(
            "center", "middle", source_width, source_height
        )
    ]
    return transformer, engine


class ExtremeAspectCropTestCase(unittest.TestCase):
    def test_wide_strip_from_square_transparent_png_is_not_empty(self):
        # /unsafe/800x20/rainbow.png: auto_crop computes crop height
        # round(16 * 20 / 800) == 0, so the crop is an empty image.
        transformer, engine = make_transformer("rainbow.png", 800, 20)

        transformer.auto_crop()

        width, height = engine.size
        self.assertGreaterEqual(height, 1, f"crop is {width}x{height}")

    def test_fit_in_width_only_on_wide_source_is_not_zero_height(self):
        # /unsafe/fit-in/100x0/940x2.png: fit_in_resize computes
        # resize height round(2 * 100 / 940) == 0, so resize gets 0 height.
        transformer, engine = make_transformer(
            "940x2.png", 100, 0, fit_in=True
        )

        transformer.fit_in_resize()

        width, height = engine.size
        self.assertGreaterEqual(height, 1, f"result is {width}x{height}")
