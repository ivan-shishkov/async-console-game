import time
import curses
import random
import asyncio

from animations import (
    animate_spaceship, animate_blinking_star, animate_gun_shot,
    animate_flying_garbage,
)
from utils import get_unique_random_numbers_pairs, get_animation_frames

TIC_TIMEOUT = 0.1

coroutines = []


async def generate_flying_garbage(canvas, garbage_frames):
    _, canvas_width = canvas.getmaxyx()

    while True:
        coroutines.append(
            animate_flying_garbage(
                canvas=canvas,
                column=random.randint(1, canvas_width - 1),
                garbage_frame=random.choice(garbage_frames),
            )
        )
        timeout = random.randint(10, 20)

        for _ in range(timeout):
            await asyncio.sleep(0)


def get_generating_flying_garbage_coroutine(canvas):
    garbage_frames = get_animation_frames(
        filenames=[
            'garbage_duck.txt',
            'garbage_hubble.txt',
            'garbage_lamp.txt',
            'garbage_large.txt',
            'garbage_small.txt',
            'garbage_xl.txt',
        ],
    )
    return generate_flying_garbage(
        canvas=canvas,
        garbage_frames=garbage_frames,
    )


def get_animated_stars_coroutines(canvas, stars_count, stars_symbols='*+.:'):
    canvas_height, canvas_width = canvas.getmaxyx()

    stars_coordinates = get_unique_random_numbers_pairs(
        first_number_range=(1, canvas_height - 2),
        second_number_range=(1, canvas_width - 2),
        count=stars_count,
    )
    return [
        animate_blinking_star(
            canvas=canvas,
            row=row,
            column=column,
            symbol=random.choice(stars_symbols),
        )
        for row, column in stars_coordinates
    ]


def get_animated_spaceship_coroutine(canvas, start_row, start_column):
    animation_frames = get_animation_frames(
        filenames=[
            'spaceship_frame_1.txt',
            'spaceship_frame_2.txt',
        ],
    )
    return animate_spaceship(
        canvas=canvas,
        start_row=start_row,
        start_column=start_column,
        frames=animation_frames,
    )


def main(canvas):
    curses.curs_set(False)

    canvas.nodelay(True)
    canvas.border()

    canvas_height, canvas_width = canvas.getmaxyx()

    center_row = (canvas_height - 1) // 2
    center_column = (canvas_width - 1) // 2

    coroutines.extend(
        get_animated_stars_coroutines(
            canvas=canvas,
            stars_count=100,
        ),
    )
    coroutines.append(
        get_animated_spaceship_coroutine(
            canvas=canvas,
            start_row=center_row + 1,
            start_column=center_column - 2,
        ),
    )
    coroutines.append(
        animate_gun_shot(
            canvas=canvas,
            start_row=center_row,
            start_column=center_column,
        ),
    )
    coroutines.append(
        get_generating_flying_garbage_coroutine(
            canvas=canvas,
        ),
    )
    while True:
        for coroutine in coroutines[:]:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
