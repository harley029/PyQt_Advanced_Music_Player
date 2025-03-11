import pytest
from interfaces.navigation.navigation import (
    NormalNavigationStrategy,
    RandomNavigationStrategy,
    LoopingNavigationStrategy,
)

# --- Тесты для NormalNavigationStrategy --- #


def test_normal_navigation_get_next_index():
    strat = NormalNavigationStrategy()
    # Если current_index=2, count=6, ожидаем 3
    assert strat.get_next_index(2, 6) == 3
    # Если current_index=5, count=6, ожидаем 0 (обёртывание)
    assert strat.get_next_index(5, 6) == 0


def test_normal_navigation_get_previous_index():
    strat = NormalNavigationStrategy()
    # Если current_index=2, count=6, предыдущий индекс должен быть 1
    assert strat.get_previous_index(2, 6) == 1
    # Если current_index=0, count=6, предыдущий индекс должен быть 5 (обёртывание)
    assert strat.get_previous_index(0, 6) == 5


def test_normal_navigation_invalid_inputs():
    strat = NormalNavigationStrategy()
    # Если current_index отрицательный
    with pytest.raises(ValueError):
        strat.get_next_index(-1, 5)
    # Если current_index равен count
    with pytest.raises(ValueError):
        strat.get_next_index(5, 5)
    # Если count <= 0
    with pytest.raises(ValueError):
        strat.get_next_index(0, 0)


# --- Тесты для RandomNavigationStrategy --- #


def test_random_navigation_get_next_index():
    strat = RandomNavigationStrategy()
    current_index = 2
    count = 6
    result = strat.get_next_index(current_index, count)
    # Проверяем, что результат находится в диапазоне
    assert 0 <= result < count
    # Если count > 1, функция должна вернуть индекс, отличный от current_index
    if count > 1:
        assert result != current_index


def test_random_navigation_get_previous_index():
    strat = RandomNavigationStrategy()
    current_index = 2
    count = 6
    result = strat.get_previous_index(current_index, count)
    # Метод get_previous_index для случайной стратегии не фильтрует результат,
    # поэтому достаточно проверить, что результат находится в диапазоне.
    assert 0 <= result < count


def test_random_navigation_invalid_inputs_get_next():
    strat = RandomNavigationStrategy()
    # Для get_next_index вызывается validate_inputs, поэтому некорректные данные должны вызывать ошибку
    with pytest.raises(ValueError):
        strat.get_next_index(-1, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(5, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(0, 0)


# Для get_previous_index в RandomNavigationStrategy в реализации не вызывается validate_inputs.
# Однако, если count <= 0, randint(0, count-1) вызовет ValueError, что можно проверить:
def test_random_navigation_invalid_inputs_get_previous():
    strat = RandomNavigationStrategy()
    with pytest.raises(ValueError):
        strat.get_previous_index(0, 0)


# --- Тесты для LoopingNavigationStrategy --- #


def test_looping_navigation_get_next_index():
    strat = LoopingNavigationStrategy()
    # Для looping стратегии следующий индекс всегда равен текущему
    assert strat.get_next_index(3, 10) == 3


def test_looping_navigation_get_previous_index():
    strat = LoopingNavigationStrategy()
    # Для looping стратегии предыдущий индекс всегда равен текущему
    assert strat.get_previous_index(3, 10) == 3


def test_looping_navigation_invalid_inputs():
    strat = LoopingNavigationStrategy()
    with pytest.raises(ValueError):
        strat.get_next_index(-1, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(5, 5)
    with pytest.raises(ValueError):
        strat.get_previous_index(0, 0)
