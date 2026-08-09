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
TOTAL_FRAMES = 180
FIRE_START = 132

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
        "       /\\                       /\\       ",
        "   ___/  \\____           ____/  \\___   ",
        "  /           \\_________/           \\  ",
        " /_____________/\\ (@::@) /\\_____________\\ ",
        "                 \\  \\//  /                 ",
        "          ________\\ (oo) /________          ",
        "         / / /     \\ VV /     \\ \\ \\         ",
        "        /_/_/       \\  /       \\_\\_\\        ",
        "                     /__\\                  ",
    ),
    (
        "                                           ",
        "    _______                   _______    ",
        " __/       \\____         ____/       \\__ ",
        "/      /\\       \\_______/       /\\      \\",
        "\\____/  \\_______/\\ (@::@) /\\_______/  \\____/",
        "                  \\  \\//  /                 ",
        "           ________\\ (oo) /________          ",
        "           \\ \\ \\   \\ VV /   / / /          ",
        "            \\_\\_\\   \\  /   /_/_/           ",
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


def dragon_position(frame: int, width: int) -> tuple[int, int]:
    span = WIDTH + width + 4
    if frame < 56:
        progress = frame / 55
        return round(-width - 2 + progress * span), 7 + round(math.sin(frame / 5))
    if frame < 112:
        progress = (frame - 56) / 55
        return WIDTH + 2 - round(progress * span), 7 + round(math.sin(frame / 5))
    if frame < FIRE_START:
        progress = (frame - 112) / (FIRE_START - 112)
        eased = progress * progress * (3 - 2 * progress)
        x = round(-width - 2 + eased * (WIDTH // 2 + width // 2 + 2))
        y = round(7 - eased * 6)
        return x, y
    return (WIDTH - width) // 2, 1


def draw_dragon(canvas: Canvas, frame: int) -> tuple[int, int]:
    art = DRAGON_FRAMES[(frame // 3) % len(DRAGON_FRAMES)]
    art_width = max(map(len, art))
    x, y = dragon_position(frame, art_width)
    mouth = (x + art_width // 2, y + 6)

    for row, source in enumerate(art):
        line = source.ljust(art_width)
        color = "dragon_bright" if row < 3 or (frame // 3 + row) % 5 == 0 else "dragon"
        canvas.text(x, y + row, line, color)
        for column, char in enumerate(source):
            if char in "@o":
                canvas.put(x + column, y + row, char, "eye")
        if "VV" in source:
            mouth = (x + source.index("VV") + 1, y + row)

    return mouth


def block_text(text: str) -> tuple[str, ...]:
    rows = []
    for row in range(5):
        rows.append(" ".join(FONT[char][row] if char != " " else "..." for char in text))
    return tuple(rows)


MESSAGE = (block_text("WELCOME TO"), block_text("MY GITHUB"))


def draw_creation_fire(canvas: Canvas, frame: int, mouth_x: int, mouth_y: int) -> None:
    age = frame - FIRE_START
    if age < 0 or age > 35:
        return

    rng = random.Random(frame * 97 + 626262)
    stream_length = min(6, age + 1)
    flame_chars = "*oO@"
    flame_colors = ("fire_yellow", "fire_yellow", "fire_orange", "fire_red")

    for distance in range(1, stream_length + 1):
        index = (distance + frame) % len(flame_chars)
        canvas.put(mouth_x + rng.choice((-1, 0, 0, 1)), mouth_y + distance, flame_chars[index], flame_colors[index])

    for center_y, delay in ((15, 6), (21, 10)):
        radius = min(32, max(0, age - delay) * 2)
        if radius == 0:
            continue
        for direction in (-1, 1):
            front_x = mouth_x + direction * radius
            canvas.put(front_x, center_y + rng.choice((-1, 0, 1)), "@", "fire_red")
            canvas.put(front_x - direction, center_y + rng.choice((-1, 0, 1)), "O", "fire_orange")
        for x in range(mouth_x - radius, mouth_x + radius + 1):
            if rng.random() < 0.08:
                canvas.put(x, center_y + rng.choice((-2, -1, 0, 1, 2)), rng.choice("~*o"), rng.choice(flame_colors[:3]))


def draw_message(canvas: Canvas, frame: int) -> None:
    age = frame - FIRE_START
    if age < 6:
        return

    for block, y, delay in ((MESSAGE[0], 13, 6), (MESSAGE[1], 19, 10)):
        width = max(map(len, block))
        x = (WIDTH - width) // 2
        for row, line in enumerate(block):
            for column, char in enumerate(line):
                reveal_age = delay + math.ceil(abs(column - width / 2) / 2)
                if char == "#" and age >= reveal_age:
                    heat = age - reveal_age
                    color = "fire_yellow" if heat < 2 else "fire_orange" if heat < 4 else "message"
                    canvas.put(x + column, y + row, "#", color)


def make_frame(frame: int) -> Canvas:
    canvas = Canvas()
    draw_sky(canvas, frame, show_moon=frame < 112)
    draw_castle(canvas)
    mouth_x, mouth_y = draw_dragon(canvas, frame)
    draw_creation_fire(canvas, frame, mouth_x, mouth_y)
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
