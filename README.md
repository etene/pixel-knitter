# Pixel Knitter

`pixel-knitter` takes a bitmap and turns it into a knitting pattern.

The output is written to stdout in self-contained html format.
It does only one thing; if you need other formats, html can be converted to pretty much everything.

## Usage

```
usage: pixel-knitter [-h] [-s {horizontal,vertical}] image

Turn a bitmap (like a PNG image) into a knitting/tricot pattern.

positional arguments:
  image                 The image to get pixels from, - for stdin.
options:
  -h, --help            show this help message and exit
  -s {horizontal,vertical}, --streak-mode {horizontal,vertical}
                        Whether to label continuous streaks of the same color horizontally or vertically.
```

## Recipes

### Generate a HTML file

```sh
pixel-knitter -s vertical image.png > generated.html
```

### Generate a PDF

```sh
pixel-knitter -s vertical image.png | wkhtmltopdf - generated.pdf
```

### Generate a PNG

```sh
pixel-knitter -s vertical image.png | wkhtmltoimage --format png - generated.png
```

### Display the pattern in the terminal using sixels

Needs a compatible terminal.

```sh
pixel-knitter -s vertical image.png | wkhtmltoimage --format png - -  | img2sixel
```
