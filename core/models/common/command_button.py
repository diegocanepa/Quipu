class CommandButton:
    def __init__(self, text: str, callback_data: str):
        """
        Initializes a CommandButton instance.

        Args:
            name (str): The name of the button.
            callback_data (str): The callback data associated with the button.
        """
        self.text = text
        self.callback_data = callback_data
