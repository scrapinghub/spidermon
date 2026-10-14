DEFAULT_LINE_LENGTH = 70
DEFAULT_LINE_CHAR = "-"
DEFAULT_LINE_BOLD_CHAR = "="
DEFAULT_LINE_LIGHT_CHAR = "-"


def line(length: int = DEFAULT_LINE_LENGTH, char: str = DEFAULT_LINE_CHAR) -> str:
    return char * length


def line_title(
    title: str,
    length: int = DEFAULT_LINE_LENGTH,
    char: str = DEFAULT_LINE_CHAR,
) -> str:
    title_length = len(title) + 2
    left_length = (length - title_length) // 2
    right_length = left_length + length - title_length - left_length * 2
    return f"{char * left_length} {title} {char * right_length}"


class Message:
    def __init__(self, text: str | None = None) -> None:
        self.msg = text or ""

    def write(self, text: str) -> None:
        self.msg += text

    def write_line(self, text: str | None = None) -> None:
        self.msg += "%s\n" % (text or "")

    def write_separator(
        self,
        length: int = DEFAULT_LINE_LENGTH,
        char: str = DEFAULT_LINE_CHAR,
    ) -> None:
        self.write_line(line(length=length, char=char))

    def write_bold_separator(self, length: int = DEFAULT_LINE_LENGTH) -> None:
        self.write_separator(length=length, char=DEFAULT_LINE_BOLD_CHAR)

    def write_light_separator(self, length: int = DEFAULT_LINE_LENGTH) -> None:
        self.write_separator(length=length, char=DEFAULT_LINE_LIGHT_CHAR)

    def __str__(self) -> str:
        return self.msg
