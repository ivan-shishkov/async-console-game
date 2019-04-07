import time
import curses
import asyncio
import random
import os.path

from curses_tools import draw_frame

TIC_TIMEOUT = 0.1


def load_text_data(filepath):
    with open(filepath, 'r') as file:
        return file.read()


def get_animation_frames(filenames, path='frames'):
    return [
        load_text_data(os.path.join(path, filename))
        for filename in filenames
    ]


async def animate_gun_shot(
        canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_blinking_star(canvas, row, column, symbol='*'):
    current_frame = random.randint(1, 4)

    while True:
        if current_frame == 1:
            canvas.addstr(row, column, symbol, curses.A_DIM)

            for _ in range(20):
                await asyncio.sleep(0)

            current_frame = 2

        if current_frame == 2:
            canvas.addstr(row, column, symbol)

            for _ in range(3):
                await asyncio.sleep(0)

            current_frame = 3

        if current_frame == 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)

            for _ in range(5):
                await asyncio.sleep(0)

            current_frame = 4

        if current_frame == 4:
            canvas.addstr(row, column, symbol)

            for _ in range(3):
                await asyncio.sleep(0)

            current_frame = 1


async def animate_spaceship(canvas, row, column, frames, frame_delay=2):
    while True:
        for frame in frames:
            draw_frame(canvas, row, column, frame)

            for _ in range(frame_delay):
                await asyncio.sleep(0)

            draw_frame(canvas, row, column, frame, negative=True)


def get_unique_numbers_pairs(first_number_range, second_number_range, count):
    numbers_pairs = set()

    first_number_min, first_number_max = first_number_range
    second_number_min, second_number_max = second_number_range

    max_pairs_count = (
            (first_number_max - first_number_min + 1) *
            (second_number_max - second_number_min + 1)
    )

    count = max_pairs_count if count > max_pairs_count else count

    while len(numbers_pairs) < count:
        first_number = random.randint(first_number_min, first_number_max)
        second_number = random.randint(second_number_min, second_number_max)

        if (first_number, second_number) not in numbers_pairs:
            numbers_pairs.add((first_number, second_number))

    return list(numbers_pairs)


def main(canvas):
    curses.curs_set(False)

    canvas.border()

    canvas_height, canvas_width = canvas.getmaxyx()

    stars_coordinates = get_unique_numbers_pairs(
        first_number_range=(1, canvas_height - 2),
        second_number_range=(1, canvas_width - 2),
        count=300,
    )

    coroutines = [
        animate_blinking_star(
            canvas=canvas,
            row=row,
            column=column,
            symbol=random.choice('*+.:'),
        )
        for row, column in stars_coordinates
    ]

    center_row = (canvas_height - 1) // 2
    center_column = (canvas_width - 1) // 2

    coroutines.append(animate_gun_shot(canvas, center_row, center_column))

    spaceship_animation_frames = get_animation_frames(
        filenames=[
            'spaceship_frame_1.txt',
            'spaceship_frame_2.txt',
        ],
    )
    coroutines.append(
        animate_spaceship(
            canvas,
            center_row,
            center_column - 2,
            spaceship_animation_frames,
        ),
    )

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
