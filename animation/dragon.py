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
HEIGHT = 34
FPS = 12
TOTAL_FRAMES = 216
FIRE_START = 132
LAND_START = 172
LAND_END = 204

COLORS = {
    "sky": "#07111f",
    "star_dim": "#52657a",
    "star": "#b8d8f0",
    "moon": "#f6e7bd",
    "dragon_dark": "#176b3a",
    "dragon_green": "#35b95f",
    "dragon_light": "#7bea72",
    "dragon_gold": "#f2c14e",
    "eye": "#fff4b0",
    "fire_red": "#ef476f",
    "fire_orange": "#ff8c42",
    "fire_yellow": "#ffe66d",
    "castle_dark": "#26364d",
    "castle_stone": "#52677f",
    "castle_light": "#71879d",
    "castle_gold": "#f5c451",
    "message": "#79e7ff",
}

DRAGON_PALETTE = {
    "g": "dragon_dark",
    "G": "dragon_green",
    "L": "dragon_light",
    "y": "dragon_gold",
    "e": "eye",
}

DRAGON_BODY = (
    "................................",
    "................................",
    "................................",
    ".........................y..y...",
    "........................yG.yG...",
    "......................gggggggg..",
    "...................ggGGGGeGGgg..",
    "..............ggGGGGGGGGGGGGGGgg",
    "g..........ggGGGGGGGLLGGGGGGGGGg",
    "gggggggggggGGGGGGGGGGGGGGGGGGgg.",
    "..ggGGGGGGGGGGGGGGGGGGGGGGGgg...",
    ".....ggGGGGGGyyyyGGGGGGGGgg.....",
    ".........ggGGyyyyGGGGgg.........",
    "...........ggGG...GGgg..........",
    "..........gg.......gg...........",
    ".........gg.........gg..........",
)

DRAGON_WINGS = (
    (
        ".............g..................",
        "............gGg.................",
        "...........gGGGg................",
        "..........gGGLGGg...............",
        ".........gGGL.LGGg..............",
        "........gGGg...gGGg.............",
        ".......gGGg.....gGGGg...........",
        ".........gg.......gg............",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
    ),
    (
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "..............gggg..............",
        "............ggGGGGgg............",
        "..........ggGGLGGGGgg...........",
        "........ggGGGg.gGGGGg...........",
        "......ggGGGg....gGGGg...........",
        ".....gGGGg.......gGGg...........",
        "....gGGg..........gg............",
        "...gGGg.........................",
        "....gg..........................",
        "................................",
    ),
)

DRAGON_WING_FOLDED = (
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    ".............gggg...............",
    "............gGGGGg..............",
    "...........gGGLLGGg.............",
    "............gGGGGg..............",
    ".............gggg...............",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
)

MOON = (
    "   _.._   ",
    " .'    `. ",
    "/  .--.  \\",
    "\\  `--'  /",
    " `-.__.-' ",
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
        self.rows = [[(" ", None, None) for _ in range(WIDTH)] for _ in range(HEIGHT)]

    def put(self, x: int, y: int, char: str, color: str) -> None:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and char != " ":
            self.rows[y][x] = (char, color, None)

    def text(self, x: int, y: int, value: str, color: str) -> None:
        for offset, char in enumerate(value):
            self.put(x + offset, y, char, color)

    def put_halves(self, x: int, y: int, top: str | None, bottom: str | None) -> None:
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or (top is None and bottom is None):
            return

        current_char, current_fg, current_bg = self.rows[y][x]
        current_top = current_fg if current_char in ("▀", "█") else None
        current_bottom = current_bg if current_char == "▀" else current_fg if current_char in ("▄", "█") else None
        top = top or current_top
        bottom = bottom or current_bottom

        if top == bottom:
            self.rows[y][x] = ("█", top, None)
        elif top and bottom:
            self.rows[y][x] = ("▀", top, bottom)
        elif top:
            self.rows[y][x] = ("▀", top, None)
        else:
            self.rows[y][x] = ("▄", bottom, None)

    def put_pixel(self, x: int, pixel_y: int, color: str) -> None:
        if pixel_y % 2 == 0:
            self.put_halves(x, pixel_y // 2, color, None)
        else:
            self.put_halves(x, pixel_y // 2, None, color)

    def pixel_sprite(
        self,
        x: int,
        y: int,
        sprite: tuple[str, ...],
        palette: dict[str, str],
        flip: bool,
    ) -> None:
        width = max(map(len, sprite))
        rows = [line.ljust(width, ".") for line in sprite]
        if flip:
            rows = [line[::-1] for line in rows]
        for pixel_y in range(0, len(rows), 2):
            top_row = rows[pixel_y]
            bottom_row = rows[pixel_y + 1] if pixel_y + 1 < len(rows) else "." * width
            for pixel_x, (top_key, bottom_key) in enumerate(zip(top_row, bottom_row)):
                self.put_halves(x + pixel_x, y + pixel_y // 2, palette.get(top_key), palette.get(bottom_key))


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
    castle_top = 52
    for x in range(WIDTH):
        for pixel_y in range(castle_top, HEIGHT * 2):
            brick_row = (pixel_y - castle_top) // 4
            offset_x = x + (brick_row % 2) * 5
            color = "castle_stone"
            if pixel_y % 4 == 0 or offset_x % 10 == 0:
                color = "castle_dark"
            elif (x * 7 + pixel_y * 3) % 29 == 0:
                color = "castle_light"
            canvas.put_pixel(x, pixel_y, color)

    for x in range(WIDTH):
        if x % 8 in (1, 2, 3, 4):
            for pixel_y in range(castle_top - 4, castle_top):
                canvas.put_pixel(x, pixel_y, "castle_stone")
            canvas.put_pixel(x, castle_top - 4, "castle_light")

    for window_x in (10, 31, 63, 82):
        canvas.put_pixel(window_x + 1, castle_top + 5, "castle_gold")
        for pixel_y in range(castle_top + 6, castle_top + 11):
            for x in range(window_x, window_x + 3):
                canvas.put_pixel(x, pixel_y, "castle_gold")

    for pixel_y in range(castle_top + 9, HEIGHT * 2):
        half_width = min(5, 2 + (pixel_y - castle_top - 9) // 2)
        for x in range(WIDTH // 2 - half_width, WIDTH // 2 + half_width + 1):
            canvas.put_pixel(x, pixel_y, "castle_dark")

    for banner_x in (24, 71):
        for pixel_y in range(castle_top - 2, castle_top + 7):
            canvas.put_pixel(banner_x, pixel_y, "castle_gold")
        canvas.put_pixel(banner_x + 1, castle_top + 5, "castle_gold")
        canvas.put_pixel(banner_x + 2, castle_top + 6, "castle_gold")


def dragon_position(frame: int, width: int) -> tuple[int, int, bool]:
    left = -width - 2
    flight_span = WIDTH + width + 4
    if frame < 56:
        progress = frame / 55
        return round(left + progress * flight_span), 8 + round(math.sin(frame / 5)), False
    if frame < 112:
        progress = (frame - 56) / 55
        return round(WIDTH + 2 - progress * flight_span), 8 + round(math.sin(frame / 5)), True
    if frame < FIRE_START:
        progress = (frame - 112) / (FIRE_START - 112)
        eased = progress * progress * (3 - 2 * progress)
        x = round(-width - 2 + eased * (width + 4))
        return x, 8 + round(math.sin(frame / 5)), False
    if frame < LAND_START:
        return 2, 8, False
    if frame < LAND_END:
        progress = (frame - LAND_START) / (LAND_END - LAND_START)
        eased = progress * progress * (3 - 2 * progress)
        arc = math.sin(math.pi * progress) * 2
        return 2, round(8 + eased * 10 - arc), False
    return 2, 18, False


def draw_dragon(canvas: Canvas, frame: int) -> tuple[int, int]:
    if frame >= LAND_END - 8:
        wing = DRAGON_WING_FOLDED
    else:
        wing = DRAGON_WINGS[(frame // 6) % len(DRAGON_WINGS)]
    width = max(map(len, DRAGON_BODY))
    x, y, flip = dragon_position(frame, width)
    canvas.pixel_sprite(x, y, wing, DRAGON_PALETTE, flip)
    canvas.pixel_sprite(x, y, DRAGON_BODY, DRAGON_PALETTE, flip)
    mouth_x = x if flip else x + width - 1
    return mouth_x, y * 2 + 8


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
    flame_colors = ("fire_yellow", "fire_yellow", "fire_orange", "fire_red")
    length = min(WIDTH - mouth_x - 1, max(0, age - 1) * 2)

    for distance in range(1, length + 1):
        spread = max(1, distance // 4)
        particles = 2 if distance < 10 else 1 + (distance + frame) % 2
        for _ in range(particles):
            pixel_y = mouth_y + rng.randint(-spread, spread)
            color = rng.choice(flame_colors[:3] if distance < length - 4 else flame_colors[2:])
            canvas.put_pixel(mouth_x + distance, pixel_y, color)


def draw_message(canvas: Canvas, frame: int) -> None:
    age = frame - FIRE_START
    if age < 2:
        return

    for block, y in ((MESSAGE[0], 7), (MESSAGE[1], 15)):
        width = max(map(len, block))
        x = 36 + (WIDTH - 36 - width) // 2
        for row, line in enumerate(block):
            for column, char in enumerate(line):
                reveal_age = 2 + math.ceil((x + column - 33) / 2)
                if char == "#" and age >= reveal_age:
                    heat = age - reveal_age
                    color = "fire_yellow" if heat < 2 else "fire_orange" if heat < 4 else "message"
                    canvas.put(x + column, y + row, "#", color)


def make_frame(frame: int) -> Canvas:
    canvas = Canvas()
    draw_sky(canvas, frame, show_moon=True)
    draw_castle(canvas)
    mouth_x, mouth_y = draw_dragon(canvas, frame)
    draw_creation_fire(canvas, frame, mouth_x, mouth_y)
    draw_message(canvas, frame)
    return canvas


def ansi_frame(canvas: Canvas, use_color: bool) -> str:
    lines = []
    for row in canvas.rows:
        output = []
        active_fg = None
        active_bg = None
        for char, foreground, background in row:
            if use_color and foreground != active_fg:
                output.append(ansi_color(foreground, background=False))
                active_fg = foreground
            if use_color and background != active_bg:
                output.append(ansi_color(background, background=True))
                active_bg = background
            output.append(char)
        if use_color:
            output.append("\033[0m")
        lines.append("".join(output).rstrip())
    return "\n".join(lines)


def ansi_color(color: str | None, background: bool) -> str:
    if color is None:
        return "\033[49m" if background else "\033[39m"
    value = COLORS[color]
    red, green, blue = (int(value[index : index + 2], 16) for index in (1, 3, 5))
    return f"\033[{48 if background else 38};2;{red};{green};{blue}m"


def play_terminal(fps: int, loops: int, use_color: bool) -> None:
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
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
            for x, (char, foreground, background) in enumerate(row):
                left = padding + x * cell_width
                top = padding + y * cell_height
                right = left + cell_width - 1
                bottom = top + cell_height - 1
                middle = top + cell_height // 2
                if char == "█" and foreground:
                    draw.rectangle((left, top, right, bottom), fill=COLORS[foreground])
                elif char == "▀" and foreground:
                    draw.rectangle((left, top, right, middle - 1), fill=COLORS[foreground])
                    if background:
                        draw.rectangle((left, middle, right, bottom), fill=COLORS[background])
                elif char == "▄" and foreground:
                    draw.rectangle((left, middle, right, bottom), fill=COLORS[foreground])
                elif foreground and char.strip():
                    draw.text((left, top), char, font=font, fill=COLORS[foreground], spacing=0)
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
