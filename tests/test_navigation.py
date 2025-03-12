import pytest
from interfaces.navigation.navigation import (
    NormalNavigationStrategy,
    RandomNavigationStrategy,
    LoopingNavigationStrategy,
)

# --- Tests for NormalNavigationStrategy --- #


def test_normal_navigation_get_next_index():
    """
    Tests that NormalNavigationStrategy.get_next_index() correctly increments the index
    and wraps around to 0 when reaching the end.

    Args:
        None

    Returns:
        None

    Assertions:
        - Index is correctly incremented for a non-boundary case
        - Index wraps to 0 when at the last position
    """
    strat = NormalNavigationStrategy()
    assert strat.get_next_index(2, 6) == 3
    assert strat.get_next_index(5, 6) == 0


def test_normal_navigation_get_previous_index():
    """
    Tests that NormalNavigationStrategy.get_previous_index() correctly decrements the index
    and wraps around to the last index when reaching 0.

    Args:
        None

    Returns:
        None

    Assertions:
        - Index is correctly decremented for a non-boundary case
        - Index wraps to the last position when at the first position
    """
    strat = NormalNavigationStrategy()
    assert strat.get_previous_index(2, 6) == 1
    assert strat.get_previous_index(0, 6) == 5


def test_normal_navigation_invalid_inputs():
    """
    Tests that NormalNavigationStrategy methods correctly raise ValueError exceptions
    when provided with invalid inputs such as negative indices, indices equal to or greater
    than the count, or zero count.

    Args:
        None

    Returns:
        None

    Raises:
        pytest.raises: Verifies ValueError is raised for:
            - Negative current index
            - Current index equal to or greater than count
            - Zero count
    """
    strat = NormalNavigationStrategy()
    with pytest.raises(ValueError):
        strat.get_next_index(-1, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(5, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(0, 0)


# --- Tests for RandomNavigationStrategy --- #


def test_random_navigation_get_next_index():
    """
    Tests that RandomNavigationStrategy.get_next_index() returns a valid index
    that is different from the current index and within the valid range.

    Args:
        None

    Returns:
        None

    Assertions:
        - Returned index is within valid range (0 <= result < count)
        - Returned index is different from current index when count > 1
    """
    strat = RandomNavigationStrategy()
    current_index = 2
    count = 6
    result = strat.get_next_index(current_index, count)
    assert 0 <= result < count
    if count > 1:
        assert result != current_index


def test_random_navigation_get_previous_index():
    """
    Tests that RandomNavigationStrategy.get_previous_index() returns a valid index
    within the valid range.

    Args:
        None

    Returns:
        None

    Assertions:
        - Returned index is within valid range (0 <= result < count)
    """
    strat = RandomNavigationStrategy()
    current_index = 2
    count = 6
    result = strat.get_previous_index(current_index, count)
    assert 0 <= result < count


def test_random_navigation_invalid_inputs_get_next():
    """
    Tests that RandomNavigationStrategy.get_next_index() correctly raises ValueError exceptions
    when provided with invalid inputs such as negative indices, indices equal to or greater
    than the count, or zero count.

    Args:
        None

    Returns:
        None

    Raises:
        pytest.raises: Verifies ValueError is raised for:
            - Negative current index
            - Current index equal to or greater than count
            - Zero count
    """
    strat = RandomNavigationStrategy()
    with pytest.raises(ValueError):
        strat.get_next_index(-1, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(5, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(0, 0)


def test_random_navigation_invalid_inputs_get_previous():
    """
    Tests that RandomNavigationStrategy.get_previous_index() correctly raises ValueError exceptions
    when provided with invalid inputs such as zero count.

    Args:
        None

    Returns:
        None

    Raises:
        pytest.raises: Verifies ValueError is raised for:
            - Zero count
    """
    strat = RandomNavigationStrategy()
    with pytest.raises(ValueError):
        strat.get_previous_index(0, 0)


# --- Tests for LoopingNavigationStrategy --- #


def test_looping_navigation_get_next_index():
    """
    Tests that LoopingNavigationStrategy.get_next_index() returns the same index,
    demonstrating the looping behavior where it stays at the current position.

    Args:
        None

    Returns:
        None

    Assertions:
        - Returned index is the same as the current index
    """
    strat = LoopingNavigationStrategy()
    assert strat.get_next_index(3, 10) == 3


def test_looping_navigation_get_previous_index():
    """
    Tests that LoopingNavigationStrategy.get_previous_index() returns the same index,
    demonstrating the looping behavior where it stays at the current position.

    Args:
        None

    Returns:
        None

    Assertions:
        - Returned index is the same as the current index
    """
    strat = LoopingNavigationStrategy()
    assert strat.get_previous_index(3, 10) == 3


def test_looping_navigation_invalid_inputs():
    """
    Tests that LoopingNavigationStrategy methods correctly raise ValueError exceptions
    when provided with invalid inputs such as negative indices, indices equal to or greater
    than the count, or zero count.

    Args:
        None

    Returns:
        None

    Raises:
        pytest.raises: Verifies ValueError is raised for:
            - Negative current index
            - Current index equal to or greater than count
            - Zero count
    """
    strat = LoopingNavigationStrategy()
    with pytest.raises(ValueError):
        strat.get_next_index(-1, 5)
    with pytest.raises(ValueError):
        strat.get_next_index(5, 5)
    with pytest.raises(ValueError):
        strat.get_previous_index(0, 0)
