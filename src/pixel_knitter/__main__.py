import argparse

from pixel_knitter import PixelKnitter, StreakMode


def get_psr() -> argparse.ArgumentParser:
    psr = argparse.ArgumentParser(
        description="Turn a bitmap (like a PNG image) "
        "into a knitting/tricot pattern."
    )
    psr.add_argument(
        "image",
        type=argparse.FileType("rb"),
        help="The image to get pixels from, - for stdin.",
    )
    psr.add_argument(
        "-s",
        "--streak-mode",
        choices=StreakMode,
        default=None,
        type=StreakMode,
        help="Whether to label continuous streaks of the same color "
        "horizontally or vertically.",
    )
    return psr


def main():
    args = get_psr().parse_args()
    maker = PixelKnitter(args.image, streak_mode=args.streak_mode)
    print(maker.render())


if __name__ == "__main__":
    main()
