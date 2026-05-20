"""Task argument validator — validates add_task arguments dict from the LLM tool call."""


class TaskParser:
    """Validates add_task arguments dict produced by the LLM's tool call.

    The LLM is instructed to return structured arguments, but its output cannot
    be fully trusted: it may omit required fields or include extra ones.

    This class checks the required field ('description') and fills in sensible
    defaults for the optional fields ('status', 'category', 'people', 'deadline').

    Owns no state. Each call to validate() is independent.
    """

    # Optional fields that the LLM may or may not include.
    _OPTIONAL_FIELDS = ("status", "category", "people", "deadline")

    # Default values to use when an optional field is absent.
    _DEFAULTS = {"status": "todo", "category": "", "people": "", "deadline": ""}

    def validate(self, arguments: dict) -> dict:
        """Validate and apply defaults to add_task arguments from the LLM.

        Args:
            arguments: Dict from LLM tool_call function arguments.
                       May be missing optional keys or contain extra keys.

        Returns:
            Clean dict with exactly these 5 keys in order:
            "description", "status", "category", "people", "deadline"

        Raises:
            ValueError: If 'description' is missing or empty.
        """
        # ******************************* START HERE *******************************
        #
        # 1. Validate that 'description' is present and non-empty.
        #    arguments.get("description") returns None if the key is missing,
        #    or "" if it exists but is an empty string. Both are invalid.
        #
        #    if not arguments.get("description"):
        #        raise ValueError("missing or empty description in task arguments")
        #
        # 2. Build and return a clean dict with all 5 expected fields.
        #    For the required field, read it directly from arguments.
        #    For each optional field, use the value from arguments if the LLM
        #    included it, otherwise fall back to the default.
        #
        #    return {
        #        "description": arguments["description"],
        #        **{
        #            field: arguments.get(field, self._DEFAULTS[field])
        #            for field in self._OPTIONAL_FIELDS
        #        },
        #    }
        #
        raise NotImplementedError("Implement validate()")
        # ******************************** END HERE ********************************
