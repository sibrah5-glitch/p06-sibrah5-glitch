# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from PIL import Image
from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerEdgeTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_round_corner_edge_is_smoothed_through_alpha(
        self,
    ):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(60,255,255,255,1)",
            mode="RGBA",
        )
        alphas = image.getchannel("A").crop((0, 0, 60, 60)).getdata()
        partial = [a for a in alphas if 0 < a < 255]
        assert partial, "no partly transparent pixels on the corner arc"

        source = Image.open(self.get_fixture_path("source.jpg")).convert("RGB")
        filtered = image.convert("RGB")
        offending = []
        for x in range(60):
            for y in range(60):
                if 0 < image.getpixel((x, y))[3] < 255:
                    got = filtered.getpixel((x, y))
                    want = source.getpixel((x, y))
                    if got != want:
                        offending.append((x, y, got, want))
        assert not offending, (
            f"{len(offending)} edge pixels darkened; first: {offending[:5]}"
        )
