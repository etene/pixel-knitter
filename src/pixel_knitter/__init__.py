from collections import Counter
from dataclasses import dataclass
import enum
from functools import cached_property
from itertools import starmap
from PIL import Image
from typing import BinaryIO, Iterator, NamedTuple

from jinja2 import Environment, PackageLoader, select_autoescape


class Color(NamedTuple):
    """Represents a RGB color."""

    red: int
    green: int
    blue: int
    alpha: int = 255  # opaque

    @property
    def css(self) -> str:
        """The CSS format for this color."""
        return f"#{self.hex}"

    @property
    def hex(self) -> str:
        return "".join(f"{i:02x}" for i in self)

    @property
    def is_transparent(self) -> bool:
        """Whether it's fully transparent."""
        return self.alpha == 0

    def __str__(self) -> str:
        return "transparent" if self.is_transparent else self.css


@dataclass
class Pixel:
    """Represents a single pixel in the image."""

    color: Color
    streak: int | None = None


Line = list[Pixel]
Lines = list[Line]


class StreakMode(enum.StrEnum):
    """Available streak modes."""

    HORIZONTAL = enum.auto()
    VERTICAL = enum.auto()


def horizontal_line_iterator(lines: Lines) -> Iterator[Line]:
    """Yields horizontal lines of pixels."""
    yield from lines


def vertical_line_iterator(lines: Lines) -> Iterator[Line]:
    """Yields vertical lines of pixels."""
    for x in range(len(lines[0])):
        yield [lines[y][x] for y in range(len(lines))]


def compute_streaks(lines: Lines, mode: StreakMode):
    """Add streak info to all pixels. Modifies them in-place."""
    if mode is StreakMode.HORIZONTAL:
        pixel_iterator = horizontal_line_iterator
    elif mode is StreakMode.VERTICAL:
        pixel_iterator = vertical_line_iterator
    for line in pixel_iterator(lines):
        # Reset streak & prev color at the beginning of lines
        streak: int = 1
        prev_color: Color | None = None
        for pixel in line:
            if (prev_color is None) or (prev_color != pixel.color):
                streak = 1
                prev_color = pixel.color
            else:
                streak += 1
            pixel.streak = streak


class PixelKnitter:
    MAX_IMAGE_SIZE = 512

    def __init__(
        self,
        image_fp: BinaryIO,
        streak_mode: StreakMode | None = StreakMode.VERTICAL,
    ) -> None:
        self.image_path = str(image_fp.name)
        self.image = Image.open(image_fp)
        too_large = any(
            (
                self.image.width > self.MAX_IMAGE_SIZE,
                self.image.height > self.MAX_IMAGE_SIZE,
            )
        )
        if too_large:
            raise ValueError(
                f"Image is too large ({'x'.join(map(str, self.image.size))})"
            )
        self.jina_env = Environment(
            loader=PackageLoader("pixel_knitter"), autoescape=select_autoescape()
        )
        self.streak_mode = streak_mode

    @cached_property
    def pixels(self) -> list[Pixel]:
        """All pixels in the image, as a list."""
        pixels = []
        for pixel_color in starmap(Color, self.image.getdata()):
            if not pixel_color.is_transparent:
                if pixel_color.alpha != 255:
                    raise ValueError(f"{pixel_color.css} is semi transparent")
            pixels.append(Pixel(color=pixel_color))
        return pixels

    @cached_property
    def color_counts(self) -> Counter[Color]:
        """A Counter of all Colors found in the image."""
        return Counter((i.color for i in self.pixels))

    @cached_property
    def color_css_classes(self) -> dict[Color, str]:
        """A mapping of Colors to css class names."""
        return {color: f"color{color.hex}" for color in self.color_counts}

    @cached_property
    def lines(self) -> Lines:
        """All of the image's lines as pixels."""
        pixel_lines: Lines = []
        for line_number in range(self.image.height):
            first_pixel = line_number * self.image.width
            last_pixel = first_pixel + self.image.width
            pixel_lines.append(self.pixels[first_pixel:last_pixel])
        if self.streak_mode:
            compute_streaks(pixel_lines, self.streak_mode)
        return pixel_lines

    def render(self) -> str:
        """Generate the html page."""
        return self.jina_env.get_template("tricot.html").render(
            pixel_lines=self.lines,
            pixel_counts=self.color_counts,
            color_classes=self.color_css_classes,
            img_size=self.image.size,
            img_name=self.image_path,
        )
