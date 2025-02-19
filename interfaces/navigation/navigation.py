from random import randint

from interfaces.interfaces import INavigationStrategy


class NormalNavigationStrategy(INavigationStrategy):
    """Нормальная навигация по списку."""

    def get_next_index(self, current_index: int, count: int) -> int:
        return (current_index + 1) % count

    def get_previous_index(self, current_index: int, count: int) -> int:
        return (current_index - 1 + count) % count


class RandomNavigationStrategy(INavigationStrategy):
    """Случайная навигация (shuffle) по списку."""

    def get_next_index(self, current_index: int, count: int) -> int:
        return randint(0, count - 1)

    def get_previous_index(self, current_index: int, count: int) -> int:
        return randint(0, count - 1)


class LoopingNavigationStrategy(INavigationStrategy):
    """Зацикленная навигация по списку."""

    def get_next_index(self, current_index: int, count: int) -> int:
        return current_index

    def get_previous_index(self, current_index: int, count: int) -> int:
        return current_index
