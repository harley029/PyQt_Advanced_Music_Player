import re


class DBUtils:
    """
    Database utility class for validating database table names.

    This class provides static methods for validating table names
    against a set of allowed characters and patterns.
    """

    @staticmethod
    def is_valid_table_name(name: str) -> bool:
        """
        Check if the table name contains only valid characters.

        Valid characters include:
        - Latin letters (a-z, A-Z)
        - Ukrainian letters (а-я, А-Я, і, І, є, Є, ї, Ї)
        - Digits (0-9)
        - Spaces
        - Underscores (_)
        - Hyphens (-)
        - Exclamation marks (!)

        Args:
            name (str): The table name to validate

        Returns:
            bool: True if the table name contains only valid characters, False otherwise
        """
        return bool(re.match(r"^[\w\d\sа-яА-ЯіІєЄїЇ!_-]+$", name))
