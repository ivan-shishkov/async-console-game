import time
import curses
import asyncio
import random
import os.path

from curses_tools import draw_frame, read_controls, get_frame_size

TIC_TIMEOUT = 0.1


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

    canvas.border()

    canvas_height, canvas_width = canvas.getmaxyx()

    center_row = (canvas_height - 1) // 2
    center_column = (canvas_width - 1) // 2

    coroutines = []

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
