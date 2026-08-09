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
TURN_END = 56
RETURN_END = 76
FIRE_START = 64
FIRE_END = FIRE_START + 36
MESSAGE_START = RETURN_END
LAND_START = 102
LAND_END = 134
STORY_END = 148
PAN_END = 178
HUD_START = 178
TYPE_START = 190
WIPE_START = 256
HUD_END = 268
CAMERA_RETURN_START = 291
CAMERA_RETURN_END = 321
TOTAL_FRAMES = CAMERA_RETURN_END
HUD_X = 6
HUD_Y = 5
HUD_WIDTH = 84
HUD_HEIGHT = 18

COLORS = {
    "sky": "#07111f",
    "star_dim": "#52657a",
    "star": "#b8d8f0",
    "moon": "#e6e0d5",
    "moon_highlight": "#fff3df",
    "moon_shadow": "#9a9da3",
    "moon_dark": "#626772",
    "moon_edge": "#333b49",
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
    "message_cooling_1": "#ffb36b",
    "message_cooling_2": "#f6d6ad",
    "message_cooling_3": "#cee9df",
    "message_cooling_4": "#9ddde8",
    "hud_shadow": "#030913",
    "hud_bg": "#0b1b2b",
    "hud_border": "#4d7594",
    "hud_prompt": "#f5c451",
    "hud_text": "#d8f3ff",
    "hud_stack": "#79e7ff",
    "hud_cursor": "#9ff7eb",
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

MOON_PALETTE = {
    "m": "moon",
    "h": "moon_highlight",
    "s": "moon_shadow",
    "d": "moon_dark",
    "e": "moon_edge",
}

MOON_PIXELS = (
    "....eeeeee....",
    "..edssmmmhee..",
    ".edsssmmmhhhe.",
    "edsssdssmhhhee",
    "edddddssmhhhee",
    "edddsssdhhhhhe",
    "eddssddssmhhhe",
    "edssddssmmhhhe",
    "edddsssmmmhhhe",
    "eddssddmmmhhhe",
    "eddddssmmmhhee",
    ".eddddssmmmhe.",
    "..edssmmmmee..",
    "....eeeeee....",
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
        self.labels: list[tuple[int, int, str, str]] = []

    def put(self, x: int, y: int, char: str, color: str) -> None:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and char != " ":
            current_char, _, current_bg = self.rows[y][x]
            background = current_bg if current_char == " " else None
            self.rows[y][x] = (char, color, background)

    def text(self, x: int, y: int, value: str, color: str) -> None:
        for offset, char in enumerate(value):
            self.put(x + offset, y, char, color)

    def label(self, x: int, y: int, value: str, color: str) -> None:
        self.labels.append((x, y, value, color))
        self.text(x, y, value, color)

    def fill_rect(self, x: int, y: int, width: int, height: int, color: str) -> None:
        for row in range(max(0, y), min(HEIGHT, y + height)):
            for column in range(max(0, x), min(WIDTH, x + width)):
                self.rows[row][column] = (" ", None, color)

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
    for _ in range(88):
        stars.append((rng.randrange(WIDTH), rng.randrange(2, HEIGHT), rng.choice((1, 1, 2)), rng.choice((".", ".", "+", "*"))))
    return tuple(stars)


STARS = make_stars()


def draw_sky(canvas: Canvas, frame: int, show_moon: bool, star_offset: int = 0, moon_offset: int = 0) -> None:
    cycle_progress = frame / (TOTAL_FRAMES - 1)
    for start_x, y, speed, char in STARS:
        x = (start_x - round(cycle_progress * WIDTH * speed)) % WIDTH
        y = (y + star_offset) % HEIGHT
        twinkle = (round(cycle_progress * 29 * 11) + start_x + y) % 11
        color = "star" if twinkle < 3 or char == "*" else "star_dim"
        canvas.put(x, y, char, color)

    if show_moon:
        canvas.pixel_sprite(79, moon_offset, MOON_PIXELS, MOON_PALETTE, flip=False)


def draw_castle(canvas: Canvas, y_offset: int = 0) -> None:
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
            canvas.put_pixel(x, pixel_y + y_offset * 2, color)

    for x in range(WIDTH):
        if x % 8 in (1, 2, 3, 4):
            for pixel_y in range(castle_top - 4, castle_top):
                canvas.put_pixel(x, pixel_y + y_offset * 2, "castle_stone")
            canvas.put_pixel(x, castle_top - 4 + y_offset * 2, "castle_light")

    for window_x in (10, 31, 63, 82):
        canvas.put_pixel(window_x + 1, castle_top + 5 + y_offset * 2, "castle_gold")
        for pixel_y in range(castle_top + 6, castle_top + 11):
            for x in range(window_x, window_x + 3):
                canvas.put_pixel(x, pixel_y + y_offset * 2, "castle_gold")

    for pixel_y in range(castle_top + 9, HEIGHT * 2):
        half_width = min(5, 2 + (pixel_y - castle_top - 9) // 2)
        for x in range(WIDTH // 2 - half_width, WIDTH // 2 + half_width + 1):
            canvas.put_pixel(x, pixel_y + y_offset * 2, "castle_dark")

    for banner_x in (24, 71):
        for pixel_y in range(castle_top - 2, castle_top + 7):
            canvas.put_pixel(banner_x, pixel_y + y_offset * 2, "castle_gold")
        canvas.put_pixel(banner_x + 1, castle_top + 5 + y_offset * 2, "castle_gold")
        canvas.put_pixel(banner_x + 2, castle_top + 6 + y_offset * 2, "castle_gold")


def dragon_position(frame: int, width: int) -> tuple[int, int, bool]:
    left = -width - 2
    right = WIDTH + 2
    flight_span = WIDTH + width + 4
    if frame < TURN_END:
        progress = frame / (TURN_END - 1)
        return round(right - progress * flight_span), 8 + round(math.sin(frame / 5)), True
    if frame < RETURN_END:
        progress = (frame - TURN_END) / (RETURN_END - TURN_END - 1)
        eased = progress * progress * (3 - 2 * progress)
        x = round(left + eased * (width + 4))
        return x, 8 + round(math.sin(frame / 5)), False
    if frame < LAND_START:
        return 2, 8, False
    if frame < LAND_END:
        progress = (frame - LAND_START) / (LAND_END - LAND_START)
        eased = progress * progress * (3 - 2 * progress)
        arc = math.sin(math.pi * progress) * 2
        return 2, round(8 + eased * 10 - arc), False
    return 2, 18, False


def draw_dragon(canvas: Canvas, frame: int, y_offset: int = 0) -> tuple[int, int]:
    if frame >= LAND_END - 8:
        wing = DRAGON_WING_FOLDED
    else:
        wing = DRAGON_WINGS[(frame // 6) % len(DRAGON_WINGS)]
    width = max(map(len, DRAGON_BODY))
    x, y, flip = dragon_position(frame, width)
    y += y_offset
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

HUD_LINES = (
    (0, 3, "$ profile --role", "hud_prompt"),
    (9, 5, "Software Engineering Student @ DHBW", "hud_text"),
    (29, 10, "$ stack --list", "hud_prompt"),
    (37, 12, "Java  |  HTML  |  CSS  |  SQL", "hud_stack"),
)


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


def draw_message(canvas: Canvas, frame: int, y_offset: int = 0) -> None:
    age = frame - MESSAGE_START
    if age < 2:
        return

    for block, y in ((MESSAGE[0], 7 + y_offset), (MESSAGE[1], 15 + y_offset)):
        width = max(map(len, block))
        x = 36 + (WIDTH - 36 - width) // 2
        for row, line in enumerate(block):
            for column, char in enumerate(line):
                reveal_age = 2 + math.ceil((x + column - 33) / 3)
                if char == "#" and age >= reveal_age:
                    if frame < FIRE_END:
                        color = "fire_yellow" if age - reveal_age < 2 else "fire_orange"
                    else:
                        cooling_age = frame - FIRE_END
                        cooling_colors = (
                            "message_cooling_1",
                            "message_cooling_2",
                            "message_cooling_3",
                            "message_cooling_4",
                        )
                        color = cooling_colors[min(3, cooling_age // 2)] if cooling_age < 8 else "message"
                    canvas.put(x + column, y + row, "#", color)


def camera_offset(frame: int) -> int:
    if frame < STORY_END:
        return 0
    if frame < PAN_END:
        progress = (frame - STORY_END) / (PAN_END - STORY_END - 1)
        eased = progress * progress * (3 - 2 * progress)
        return round(eased * HEIGHT)
    if frame < CAMERA_RETURN_START:
        return HEIGHT
    if frame >= CAMERA_RETURN_END:
        return 0
    progress = (frame - CAMERA_RETURN_START) / (CAMERA_RETURN_END - CAMERA_RETURN_START - 1)
    eased = progress * progress * (3 - 2 * progress)
    return round((1 - eased) * HEIGHT)


def draw_hud_frame(canvas: Canvas, visible_height: int) -> None:
    visible_height = max(2, min(HUD_HEIGHT, visible_height))
    top = HUD_Y + (HUD_HEIGHT - visible_height) // 2
    canvas.fill_rect(HUD_X + 1, top + 1, HUD_WIDTH, visible_height, "hud_shadow")
    canvas.fill_rect(HUD_X, top, HUD_WIDTH, visible_height, "hud_bg")

    if visible_height == HUD_HEIGHT:
        prefix = "+-- PROFILE.TERM "
        top_border = prefix + "-" * (HUD_WIDTH - len(prefix) - 1) + "+"
    else:
        top_border = "+" + "-" * (HUD_WIDTH - 2) + "+"
    canvas.text(HUD_X, top, top_border, "hud_border")
    canvas.text(HUD_X, top + visible_height - 1, "+" + "-" * (HUD_WIDTH - 2) + "+", "hud_border")
    for row in range(top + 1, top + visible_height - 1):
        canvas.put(HUD_X, row, "|", "hud_border")
        canvas.put(HUD_X + HUD_WIDTH - 1, row, "|", "hud_border")
    if visible_height == HUD_HEIGHT:
        canvas.text(HUD_X + 2, HUD_Y + 8, "-" * (HUD_WIDTH - 4), "hud_border")


def draw_hud(canvas: Canvas, frame: int) -> None:
    if frame < HUD_START:
        return
    if frame >= WIPE_START:
        if frame >= HUD_END:
            return
        progress = (frame - WIPE_START + 1) / (HUD_END - WIPE_START)
        visible_height = round(HUD_HEIGHT * (1 - progress))
        if visible_height >= 2:
            draw_hud_frame(canvas, visible_height)
        return
    if frame < TYPE_START:
        progress = (frame - HUD_START + 1) / (TYPE_START - HUD_START)
        draw_hud_frame(canvas, round(HUD_HEIGHT * progress))
        return

    draw_hud_frame(canvas, HUD_HEIGHT)
    age = frame - TYPE_START
    visible_lines = []
    for start, row, text, color in HUD_LINES:
        visible = max(0, min(len(text), (age - start + 1) * 2))
        if visible:
            visible_lines.append((start, row, text[:visible], color))

    active_start = max((line[0] for line in visible_lines), default=-1)
    for start, row, text, color in visible_lines:
        if start == active_start and (frame // 6) % 2 == 0:
            text += "_"
        canvas.label(HUD_X + 4, HUD_Y + row, text, color)


def make_frame(frame: int) -> Canvas:
    canvas = Canvas()
    offset = camera_offset(frame)
    scene_frame = 0 if frame >= CAMERA_RETURN_START else min(frame, STORY_END - 1)
    show_moon = frame >= STORY_END
    moon_offset = round(-7 + 7 * offset / HEIGHT)
    draw_sky(canvas, frame, show_moon=show_moon, star_offset=offset // 4, moon_offset=moon_offset)
    draw_castle(canvas, y_offset=offset)
    mouth_x, mouth_y = draw_dragon(canvas, scene_frame, y_offset=offset)
    draw_creation_fire(canvas, scene_frame, mouth_x, mouth_y)
    draw_message(canvas, scene_frame, y_offset=offset)
    draw_hud(canvas, frame)
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
    hud_font = ImageFont.truetype(find_font(font_path), 22)
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
        label_cells = {
            (label_x + offset, label_y)
            for label_x, label_y, text, _ in canvas.labels
            for offset in range(len(text))
        }
        for y, row in enumerate(canvas.rows):
            for x, (char, foreground, background) in enumerate(row):
                left = padding + x * cell_width
                top = padding + y * cell_height
                right = left + cell_width - 1
                bottom = top + cell_height - 1
                middle = top + cell_height // 2
                if (x, y) in label_cells:
                    if background:
                        draw.rectangle((left, top, right, bottom), fill=COLORS[background])
                elif char == "█" and foreground:
                    draw.rectangle((left, top, right, bottom), fill=COLORS[foreground])
                elif char == "▀" and foreground:
                    draw.rectangle((left, top, right, middle - 1), fill=COLORS[foreground])
                    if background:
                        draw.rectangle((left, middle, right, bottom), fill=COLORS[background])
                elif char == "▄" and foreground:
                    draw.rectangle((left, middle, right, bottom), fill=COLORS[foreground])
                else:
                    if background:
                        draw.rectangle((left, top, right, bottom), fill=COLORS[background])
                    if foreground and char.strip():
                        draw.text((left, top), char, font=font, fill=COLORS[foreground], spacing=0)

        for x, y, text, color in canvas.labels:
            draw.text(
                (padding + x * cell_width, padding + y * cell_height),
                text,
                font=hud_font,
                fill=COLORS[color],
                spacing=0,
            )
        frames.append(image.quantize(palette=palette, dither=Image.Dither.NONE))

    output.parent.mkdir(parents=True, exist_ok=True)
    frame_durations = [
        (round((index + 1) * 100 / fps) - round(index * 100 / fps)) * 10
        for index in range(TOTAL_FRAMES)
    ]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=frame_durations,
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
