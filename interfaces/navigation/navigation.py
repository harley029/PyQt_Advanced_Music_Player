from random import randint

from interfaces.interfaces import INavigationStrategy


class NavigationValidation:
    """
    Base class for navigation strategies implementing common functionality.

    Provides validation and initialization methods that are common across
    all navigation strategies.
    """

    def validate_inputs(self, current_index: int, count: int) -> None:
        """
        Validate navigation input parameters.

        Args:
            current_index: Current position index
            count: Total number of items

        Raises:
            ValueError: If inputs are invalid
        """
        if count <= 0:
            raise ValueError("Count must be greater than 0")
        if current_index < 0:
            raise ValueError("Current index cannot be negative")
        if current_index >= count:
            raise ValueError(
                f"Current index {current_index} must be less than count {count}"
            )


class NormalNavigationStrategy(INavigationStrategy, NavigationValidation):
    """
    A strategy for normal sequential navigation through a list.

    This strategy implements forward and backward navigation by moving
    to the next or previous index in sequence, wrapping around at the list boundaries.

    Implements INavigationStrategy interface.
    """

    def get_next_index(self, current_index: int, count: int) -> int:
        """
        Calculate the next index in normal sequential navigation.

        Args:
            current_index (int): The current position in the list (0-based).
            count (int): The total number of items in the list.

        Returns:
            int: The next index, wrapping to 0 if exceeding count.

        Raises:
            ValueError: If inputs are invalid

        Example:
            If current_index is 5 and count is 6, returns 0.
            If current_index is 2 and count is 6, returns 3.
        """
        self.validate_inputs(current_index, count)
        return (current_index + 1) % count

    def get_previous_index(self, current_index: int, count: int) -> int:
        """
        Calculate the previous index in normal sequential navigation.

        Args:
            current_index (int): The current position in the list (0-based).
            count (int): The total number of items in the list.

        Returns:
            int: The previous index, wrapping to count-1 if going below 0.

        Raises:
            ValueError: If inputs are invalid

        Example:
            If current_index is 0 and count is 6, returns 5.
            If current_index is 3 and count is 6, returns 2.
        """
        self.validate_inputs(current_index, count)
        return (current_index - 1 + count) % count


class RandomNavigationStrategy(INavigationStrategy, NavigationValidation):
    """
    A strategy for random (shuffle) navigation through a list.

    This strategy implements navigation by randomly selecting any valid index,
    regardless of the current position. Both forward and backward navigation
    produce random results.

    Implements INavigationStrategy interface.
    """

    def get_next_index(self, current_index: int, count: int) -> int:
        """
        Get a random index for forward navigation.

        Args:
            current_index (int): The current position in the list (unused in random strategy).
            count (int): The total number of items in the list.

        Returns:
            int: A random index between 0 and count-1, inclusive.

        Raises:
            ValueError: If inputs are invalid

        Note:
            The returned index may be the same as current_index by chance.
        """
        self.validate_inputs(current_index, count)
        new_index = randint(0, count - 1)
        # Ensure we don't get the same index twice in a row
        while count > 1 and new_index == current_index:
            new_index = randint(0, count - 1)
        return new_index

    def get_previous_index(self, current_index: int, count: int) -> int:
        """
        Get a random index for backward navigation.

        Args:
            current_index (int): The current position in the list (unused in random strategy).
            count (int): The total number of items in the list.

        Returns:
            int: A random index between 0 and count-1, inclusive.

        Raises:
            ValueError: If inputs are invalid

        Note:
            Functionally identical to get_next_index as both provide random indices.
        """
        return randint(0, count - 1)


class LoopingNavigationStrategy(INavigationStrategy, NavigationValidation):
    """
    A strategy for looping navigation that stays at the current position.

    This strategy implements a static navigation pattern where both forward
    and backward navigation return to the same index, creating a loop at
    the current position.

    Implements INavigationStrategy interface.
    """

    def get_next_index(self, current_index: int, count: int) -> int:
        """
        Return the same index for forward navigation, creating a loop.

        Args:
            current_index (int): The current position in the list.
            count (int): The total number of items in the list (unused in looping strategy).

        Returns:
            int: The same index as current_index, creating a loop.
        Raises:
            ValueError: If inputs are invalid
        """
        self.validate_inputs(current_index, count)
        return current_index

    def get_previous_index(self, current_index: int, count: int) -> int:
        """
        Return the same index for backward navigation, creating a loop.

        Args:
            current_index (int): The current position in the list.
            count (int): The total number of items in the list (unused in looping strategy).

        Returns:
            int: The same index as current_index, creating a loop.
        Raises:
            ValueError: If inputs are invalid
        """
        self.validate_inputs(current_index, count)
        return current_index
