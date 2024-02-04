from io import BufferedReader
from operator import mul
from typing import Generator
from pixel_knitter import PixelKnitter, StreakMode
from pathlib import Path
import pytest
from lxml.html import document_fromstring, HtmlElement

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(params=["flower.png", "star.png"])
def image_fp(request) -> Generator[BufferedReader, None, None]:
    with DATA_DIR.joinpath(request.param).open("rb") as fp:
        yield fp


@pytest.mark.parametrize("streak_mode", (
        StreakMode.HORIZONTAL,
        StreakMode.VERTICAL,
        None,
))
def test_table_cells(image_fp: BufferedReader, streak_mode: StreakMode | None):
    knitter = PixelKnitter(image_fp=image_fp, streak_mode=streak_mode)
    html = knitter.render()
    assert knitter.pixels
    parsed = document_fromstring(html)
    table_cells = parsed.xpath(".//td")
    assert isinstance(table_cells, list)
    assert len(table_cells) == mul(*knitter.image.size)
    for td, pixel in zip(table_cells, knitter.pixels):
        assert isinstance(td, HtmlElement)
        if streak_mode:
            assert pixel.streak is not None and pixel.streak > 0
            assert int(td.text) == pixel.streak
        else:
            assert pixel.streak is None
            assert not td.text.strip()
        assert pixel.color.css == td.attrib["title"]
        assert knitter.color_css_classes[pixel.color] == td.attrib["class"]


def test_color_blocks(image_fp: BufferedReader):
    knitter = PixelKnitter(image_fp=image_fp, streak_mode=None)
    html = knitter.render()
    parsed = document_fromstring(html)
    figures = parsed.xpath(".//figure")
    assert isinstance(figures, list)
    assert len(figures) == len(knitter.color_counts)
    for i in figures:
        color_block, caption = list(i)
        assert isinstance(color_block, HtmlElement)
        assert isinstance(caption, HtmlElement)
        assert color_block.attrib["title"]
        assert caption.text
        # TODO more


def test_image_too_large(image_fp: BufferedReader,
                         monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(PixelKnitter, "MAX_IMAGE_SIZE", 1)
    with pytest.raises(ValueError) as err:
        PixelKnitter(image_fp=image_fp)
    assert str(err.value).startswith("Image is too large")
