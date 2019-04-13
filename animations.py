import asyncio
import curses
import random

from curses_tools import draw_frame, get_frame_size, read_controls
from physics import update_speed
from utils import limit


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def animate_flying_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start.
    """
    canvas_height, canvas_width = canvas.getmaxyx()

    frame_height, frame_width = get_frame_size(garbage_frame)

    column = limit(
        value=column,
        min_value=1,
        max_value=canvas_width - frame_width - 1,
    )
    row = 1

    while row < canvas_height - frame_height - 1:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


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
            await sleep(20)
            current_frame = 2

        if current_frame == 2:
            canvas.addstr(row, column, symbol)
            await sleep(3)
            current_frame = 3

        if current_frame == 3:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await sleep(5)
            current_frame = 4

        if current_frame == 4:
            canvas.addstr(row, column, symbol)
            await sleep(3)
            current_frame = 1


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column

    row_speed = column_speed = 0

    canvas_height, canvas_width = canvas.getmaxyx()

    while True:
        for frame in frames:
            rows_direction, columns_direction, _ = read_controls(canvas)

            row_speed, column_speed = update_speed(
                row_speed=row_speed,
                column_speed=column_speed,
                rows_direction=rows_direction,
                columns_direction=columns_direction,
            )
            row += row_speed
            column += column_speed

            frame_height, frame_width = get_frame_size(frame)

            row = limit(
                value=row,
                min_value=1,
                max_value=canvas_height - frame_height - 1,
            )
            column = limit(
                value=column,
                min_value=1,
                max_value=canvas_width - frame_width - 1,
            )

            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)
