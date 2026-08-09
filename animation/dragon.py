#!/usr/bin/env python3
"""Animate a flying ASCII dragon in a terminal or render it as a GIF."""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
import time
from pathlib import Path

WIDTH = 96
HEIGHT = 30
FPS = 12
TOTAL_FRAMES = 120

COLORS = {
    "sky": "#07111f",
    "star_dim": "#52657a",
    "star": "#b8d8f0",
    "moon": "#f6e7bd",
    "dragon": "#4fd1c5",
    "dragon_bright": "#9ff7eb",
    "eye": "#ffe66d",
    "fire_red": "#ef476f",
    "fire_orange": "#ff8c42",
    "fire_yellow": "#ffe66d",
    "castle": "#41536b",
    "message": "#79e7ff",
}

ANSI = {
    "star_dim": "\033[38;5;60m",
    "star": "\033[38;5;153m",
    "moon": "\033[38;5;229m",
    "dragon": "\033[38;5;43m",
    "dragon_bright": "\033[38;5;159m",
    "eye": "\033[38;5;221m",
    "fire_red": "\033[38;5;197m",
    "fire_orange": "\033[38;5;208m",
    "fire_yellow": "\033[38;5;226m",
    "castle": "\033[38;5;60m",
    "message": "\033[38;5;117m",
}

DRAGON_FRAMES = (
    (
        "              /\\                       ",
        "         ____/  \\____                   ",
        "    ____/            \\_____             ",
        " __/     _      _          `-.          ",
        "<__     / \\____/ \\            \\         ",
        "   `-._/    /\\    \\____        |        ",
        "       \\___/  \\_______ `-.___  /         ",
        "          / /\\ \\          `-<__           ",
        "         /_/  \\_\\       .-(o  o)==>      ",
        "                         /  \\__/           ",
        "                         \\__/              ",
    ),
    (
        "                                         ",
        "    ____                                 ",
        " __/    \\_____              ____        ",
        "<__     _      `------------'   `-.     ",
        "   `-._/ \\____      ____          \\     ",
        "       \\      \\____/    \\          |    ",
        "        \\____/ /\\        \\___.----'     ",
        "             _/  \\_        `-<__        ",
        "            / /\\ \\ \\     .-(o  o)==>  ",
        "           /_/  \\_\\_\\   /  \\__/       ",
        "                         \\__/              ",
    ),
)

MOON = (
    "   _.._   ",
    " .'    `. ",
    "/  .--.  \\",
    "\\  `--'  /",
    " `-.__.-' ",
)

CASTLE = (
    "        |>>>                    |>>>                    |>>>",
    "        |                       |                       |",
    "     _  |_  _              _  _|_  _              _  |_  _",
    "    | |_| |_| |            | |_| |_| |            | |_| |_| |",
    "____|         |____________|         |____________|         |____",
)

FONT = {
    "A": (".###.", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "####.", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", ".####"),
    "E": ("#####", "#....", "####.", "#....", "#####"),
    "G": (".####", "#....", "#.###", "#...#", ".###."),
    "H": ("#...#", "#...#", "#####", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "#####"),
    "L": ("#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", ".###."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", ".###."),
    "W": ("#...#", "#...#", "#.#.#", "##.##", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#.."),
}


class Canvas:
    def __init__(self) -> None:
        self.rows = [[(" ", "sky") for _ in range(WIDTH)] for _ in range(HEIGHT)]

    def put(self, x: int, y: int, char: str, color: str) -> None:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and char != " ":
            self.rows[y][x] = (char, color)

    def text(self, x: int, y: int, value: str, color: str) -> None:
        for offset, char in enumerate(value):
            self.put(x + offset, y, char, color)


def mirror(line: str) -> str:
    swaps = str.maketrans("/\\<>()[]{}", "\\/><)(][}{")
    return line[::-1].translate(swaps)


def make_stars() -> tuple[tuple[int, int, int, str], ...]:
    rng = random.Random(626262)
    stars = []
    for _ in range(62):
        stars.append((rng.randrange(WIDTH), rng.randrange(2, 24), rng.choice((1, 1, 2)), rng.choice((".", ".", "+", "*"))))
    return tuple(stars)


STARS = make_stars()


def draw_sky(canvas: Canvas, frame: int, show_moon: bool) -> None:
    for start_x, y, speed, char in STARS:
        x = (start_x - (frame * speed) // 3) % WIDTH
        twinkle = (frame + start_x + y) % 11
        color = "star" if twinkle < 3 or char == "*" else "star_dim"
        canvas.put(x, y, char, color)

    if show_moon:
        for row, line in enumerate(MOON):
            canvas.text(76, 2 + row, line, "moon")


def draw_castle(canvas: Canvas) -> None:
    x = (WIDTH - max(map(len, CASTLE))) // 2
    for row, line in enumerate(CASTLE):
        canvas.text(x, HEIGHT - len(CASTLE) + row, line, "castle")


def dragon_position(frame: int, width: int) -> tuple[int, bool]:
    if frame < 40:
        progress, facing_right = frame / 39, True
    elif frame < 80:
        progress, facing_right = (frame - 40) / 39, False
    else:
        progress, facing_right = (frame - 80) / 19, True

    span = WIDTH + width + 4
    x = round(-width - 2 + progress * span)
    if not facing_right:
        x = WIDTH + 2 - round(progress * span)
    return x, facing_right


def draw_fire(canvas: Canvas, origin_x: int, origin_y: int, facing_right: bool, frame: int, strength: int) -> None:
    if strength <= 0:
        return
    direction = 1 if facing_right else -1
    chars = "~*oO@"
    colors = ("fire_yellow", "fire_yellow", "fire_orange", "fire_orange", "fire_red")
    rng = random.Random(frame * 97 + 626262)

    for distance in range(1, strength + 1):
        spread = max(1, distance // 6)
        y = origin_y + rng.randint(-spread, spread)
        index = min(len(chars) - 1, distance * len(chars) // max(1, strength + 1))
        canvas.put(origin_x + direction * distance, y, chars[index], colors[index])
        if distance > 5 and distance % 3 == 0:
            canvas.put(origin_x + direction * distance, y + rng.choice((-1, 1)), ".", "fire_red")


def draw_dragon(canvas: Canvas, frame: int) -> None:
    art = DRAGON_FRAMES[(frame // 3) % len(DRAGON_FRAMES)]
    art_width = max(map(len, art))
    x, facing_right = dragon_position(frame, art_width)
    y = 14 + round(math.sin(frame / 4) * 0.8)

    for row, source in enumerate(art):
        line = source.ljust(art_width)
        if not facing_right:
            line = mirror(line)
        color = "dragon_bright" if row < 3 or (frame // 3 + row) % 5 == 0 else "dragon"
        canvas.text(x, y + row, line, color)

    head_x = x + art_width - 1 if facing_right else x
    canvas.put(head_x - (5 if facing_right else -5), y + 8, "o", "eye")

    local = frame % 40
    strength = 0
    if 20 <= local <= 30:
        strength = min(local - 18, 32 - local) * 2
    if frame >= 84:
        strength = min(22, max(0, frame - 83) * 2)
    draw_fire(canvas, head_x, y + 8, facing_right, frame, strength)


def block_text(text: str) -> tuple[str, ...]:
    rows = []
    for row in range(5):
        rows.append(" ".join(FONT[char][row] if char != " " else "..." for char in text))
    return tuple(rows)


MESSAGE = (block_text("WELCOME TO"), block_text("MY GITHUB"))


def draw_message(canvas: Canvas, frame: int) -> None:
    reveal = max(0.0, min(1.0, (frame - 88) / 16))
    if reveal <= 0:
        return

    for block, y in zip(MESSAGE, (3, 10)):
        width = max(map(len, block))
        visible = round(width * reveal)
        x = (WIDTH - width) // 2
        for row, line in enumerate(block):
            for column, char in enumerate(line):
                if column < visible and char == "#":
                    canvas.put(x + column, y + row, "#", "message")


def make_frame(frame: int) -> Canvas:
    canvas = Canvas()
    draw_sky(canvas, frame, show_moon=frame < 88)
    draw_castle(canvas)
    if frame < 100:
        draw_dragon(canvas, frame)
    draw_message(canvas, frame)
    return canvas


def ansi_frame(canvas: Canvas, use_color: bool) -> str:
    lines = []
    for row in canvas.rows:
        output = []
        active = None
        for char, color in row:
            next_color = color if color != "sky" else None
            if use_color and next_color != active:
                output.append(ANSI.get(next_color, "\033[0m"))
                active = next_color
            output.append(char)
        if use_color:
            output.append("\033[0m")
        lines.append("".join(output).rstrip())
    return "\n".join(lines)


def play_terminal(fps: int, loops: int, use_color: bool) -> None:
    os.system("")
    delay = 1 / fps
    sys.stdout.write("\033[2J\033[H\033[?25l")
    sys.stdout.flush()
    try:
        for _ in range(loops):
            for frame in range(TOTAL_FRAMES):
                started = time.perf_counter()
                sys.stdout.write("\033[H" + ansi_frame(make_frame(frame), use_color))
                sys.stdout.flush()
                time.sleep(max(0, delay - (time.perf_counter() - started)))
    finally:
        sys.stdout.write("\033[0m\033[?25h\n")
        sys.stdout.flush()


def find_font(explicit: str | None) -> str:
    candidates = (
        explicit,
        r"C:\Windows\Fonts\consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return "DejaVuSansMono.ttf"


def render_gif(output: Path, fps: int, font_path: str | None) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as error:
        raise SystemExit("GIF rendering requires Pillow: python -m pip install Pillow") from error

    font = ImageFont.truetype(find_font(font_path), 16)
    cell_width = math.ceil(font.getlength("M"))
    cell_height = 18
    padding = 16
    size = (WIDTH * cell_width + padding * 2, HEIGHT * cell_height + padding * 2)
    frames = []

    palette = Image.new("P", (1, 1))
    palette_values = []
    for value in COLORS.values():
        palette_values.extend(int(value[index : index + 2], 16) for index in (1, 3, 5))
    palette.putpalette(palette_values + [0] * (768 - len(palette_values)))

    for frame_number in range(TOTAL_FRAMES):
        canvas = make_frame(frame_number)
        image = Image.new("RGB", size, COLORS["sky"])
        draw = ImageDraw.Draw(image)
        for y, row in enumerate(canvas.rows):
            x = 0
            while x < WIDTH:
                color = row[x][1]
                end = x + 1
                while end < WIDTH and row[end][1] == color:
                    end += 1
                value = "".join(char for char, _ in row[x:end])
                if color != "sky" and value.strip():
                    draw.text((padding + x * cell_width, padding + y * cell_height), value, font=font, fill=COLORS[color], spacing=0)
                x = end
        frames.append(image.quantize(palette=palette, dither=Image.Dither.NONE))

    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / fps),
        loop=0,
        disposal=2,
        optimize=True,
    )
    print(f"Rendered {output} ({size[0]}x{size[1]}, {TOTAL_FRAMES} frames)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fps", type=int, default=FPS, choices=range(1, 31), metavar="1-30")
    parser.add_argument("--loops", type=int, default=1)
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--render-gif", type=Path, metavar="PATH")
    parser.add_argument("--font", help="Path to a monospace TrueType font")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.loops < 1:
        raise SystemExit("--loops must be at least 1")
    if args.render_gif:
        render_gif(args.render_gif, args.fps, args.font)
    else:
        play_terminal(args.fps, args.loops, not args.no_color)


if __name__ == "__main__":
    main()
