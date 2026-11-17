from io import BytesIO

from PIL import Image, ImageDraw
from tornado.testing import AsyncTestCase

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_source_gif():
    img = Image.new("P", (40, 40), 0)
    img.putpalette([0, 0, 0, 0, 0, 255] + [0, 0, 0] * 254)
    ImageDraw.Draw(img).ellipse((5, 5, 35, 35), fill=1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


class GifTransparencyTestCase(AsyncTestCase):
    def test_resized_gif_keeps_transparent_index(self):
        config = Config(
            PILLOW_PRESERVE_INDEXED_MODE=True,
            ALLOW_ANIMATED_GIFS=False,
        )
        engine = Engine(Context(config=config))
        engine.extension = ".gif"
        engine.image = engine.create_image(make_source_gif())

        engine.resize(20, 20)
        result = engine.read(extension=".gif")

        out = Image.open(BytesIO(result))
        self.assertIsNotNone(out.info.get("transparency"))
        alpha = out.convert("RGBA").getchannel("A")
        self.assertGreater(alpha.histogram()[0], 0)
