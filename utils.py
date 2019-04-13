import random
import os.path


def load_text_data(filepath):
    with open(filepath, 'r') as file:
        return file.read()


def get_animation_frames(filenames, path='frames'):
    return [
        load_text_data(os.path.join(path, filename))
        for filename in filenames
    ]


def limit(value, min_value, max_value):
    """Limit value by min_value and max_value."""

    return min(max_value, max(min_value, value))


def get_unique_random_numbers_pairs(
        first_number_range, second_number_range, count):
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

        numbers_pair = (first_number, second_number)

        if numbers_pair not in numbers_pairs:
            numbers_pairs.add(numbers_pair)

    return list(numbers_pairs)
