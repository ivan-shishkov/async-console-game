import time
import curses
import random
import asyncio

from utils import get_unique_random_numbers_pairs, get_animation_frames, limit
from curses_tools import draw_frame, get_frame_size, read_controls
from physics import update_speed
from obstacles import Obstacle
from explosion import explode

TIC_TIMEOUT = 0.1

PHRASES = {
    1957: 'First Sputnik',
    1961: 'Gagarin flew!',
    1969: 'Armstrong got on the moon!',
    1971: 'First orbital space station Salute-1',
    1981: 'Flight of the Shuttle Columbia',
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: 'Take the plasma gun! Shoot the garbage!',
}

year = 1957

coroutines = []

spaceship_frame = None

obstacles = []
obstacles_in_last_collisions = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def update_year(increment_value=1, update_interval=15):
    global year

    while True:
        await sleep(update_interval)

        year += increment_value


async def show_year(canvas, update_interval=15):
    while True:
        phrase = PHRASES.get(year, '')
        text = f'{year} - {phrase}' if phrase else f'{year}'

        draw_frame(canvas, 1, 1, text)
        await sleep(update_interval)
        draw_frame(canvas, 1, 1, text, negative=True)


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
        obstacle = Obstacle(
            row=row,
            column=column,
            rows_size=frame_height,
            columns_size=frame_width,
        )
        obstacles.append(obstacle)

        draw_frame(canvas, row, column, garbage_frame)
        await sleep()
        draw_frame(canvas, row, column, garbage_frame, negative=True)

        obstacles.remove(obstacle)

        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            await explode(
                canvas=canvas,
                center_row=row + frame_height // 2,
                center_column=column + frame_width // 2,
            )
            return

        row += speed


async def animate_gun_shot(
        canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep()

    canvas.addstr(round(row), round(column), 'O')
    await sleep()
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(
                    obj_corner_row=row, obj_corner_column=column):
                obstacles_in_last_collisions.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await sleep()
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


async def run_spaceship(
        canvas, start_row, start_column, gun_activation_year=2020):
    row, column = start_row, start_column

    row_speed = column_speed = 0

    canvas_height, canvas_width = canvas.getmaxyx()

    while True:
        current_frame = spaceship_frame

        rows_direction, columns_direction, space_pressed = read_controls(
            canvas=canvas,
        )
        row_speed, column_speed = update_speed(
            row_speed=row_speed,
            column_speed=column_speed,
            rows_direction=rows_direction,
            columns_direction=columns_direction,
        )
        row += row_speed
        column += column_speed

        frame_height, frame_width = get_frame_size(current_frame)

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

        draw_frame(canvas, row, column, current_frame)

        if space_pressed and row > 1 and year >= gun_activation_year:
            coroutines.append(
                animate_gun_shot(
                    canvas=canvas,
                    start_row=row - 1,
                    start_column=column + 2,
                )
            )

        await sleep()
        draw_frame(canvas, row, column, current_frame, negative=True)

        for obstacle in obstacles:
            if obstacle.has_collision(
                    obj_corner_row=row, obj_corner_column=column):
                coroutines.append(
                    show_gameover(canvas=canvas),
                )
                return


async def animate_spaceship(frames):
    global spaceship_frame

    while True:
        for frame in frames:
            spaceship_frame = frame
            await sleep()


async def generate_flying_garbage(canvas, garbage_frames):
    _, canvas_width = canvas.getmaxyx()

    while True:
        delay_tics = get_generating_garbage_delay_tics(year)

        if delay_tics:
            coroutines.append(
                animate_flying_garbage(
                    canvas=canvas,
                    column=random.randint(1, canvas_width - 1),
                    garbage_frame=random.choice(garbage_frames),
                )
            )
            await sleep(delay_tics)
        else:
            await sleep()


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


def get_animated_spaceship_coroutine():
    animation_frames = get_animation_frames(
        filenames=[
            'spaceship_frame_1.txt',
            'spaceship_frame_2.txt',
        ],
    )
    return animate_spaceship(
        frames=animation_frames,
    )


async def show_gameover(canvas):
    text = """\
   _____                         ____                 
  / ____|                       / __ \                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \ / _ \ | |  | \ \ / / _ \ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\ V /  __/ |   
  \_____|\__,_|_| |_| |_|\___|  \____/  \_/ \___|_|   
"""
    canvas_height, canvas_width = canvas.getmaxyx()

    center_row = (canvas_height - 1) // 2
    center_column = (canvas_width - 1) // 2

    frame_height, frame_width = get_frame_size(text)

    while True:
        draw_frame(
            canvas=canvas,
            start_row=center_row - frame_height // 2,
            start_column=center_column - frame_width // 2,
            text=text,
        )
        await sleep()


def get_generating_garbage_delay_tics(current_year):
    if current_year < 1961:
        return None
    elif current_year < 1969:
        return 20
    elif current_year < 1981:
        return 14
    elif current_year < 1995:
        return 10
    elif current_year < 2010:
        return 8
    elif current_year < 2020:
        return 6
    else:
        return 2


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
        get_animated_spaceship_coroutine(),
    )
    coroutines.append(
        run_spaceship(
            canvas=canvas,
            start_row=center_row + 1,
            start_column=center_column - 2,
        ),
    )
    coroutines.append(
        get_generating_flying_garbage_coroutine(
            canvas=canvas,
        ),
    )
    coroutines.append(update_year())
    coroutines.append(show_year(canvas))

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
