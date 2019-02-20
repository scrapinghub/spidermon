DEFAULT_LINE_LENGTH = 70
DEFAULT_LINE_CHAR = "-"
DEFAULT_LINE_BOLD_CHAR = "="
DEFAULT_LINE_LIGHT_CHAR = "-"


def line(length=DEFAULT_LINE_LENGTH, char=DEFAULT_LINE_CHAR):
    return char * length


def line_title(title, length=DEFAULT_LINE_LENGTH, char=DEFAULT_LINE_CHAR):
    title_length = len(title) + 2
    left_length = (length - title_length) // 2
    right_length = left_length + length - title_length - left_length * 2
    return "%s %s %s" % (char * left_length, title, char * right_length)


class Message(object):
    def __init__(self, text=None):
        self.msg = text or ""

    def write(self, text):
        self.msg += text

    def write_line(self, text=None):
        self.msg += "%s\n" % (text or "")

    def write_separator(self, length=DEFAULT_LINE_LENGTH, char=DEFAULT_LINE_CHAR):
        self.write_line(line(length=length, char=char))

    def write_bold_separator(self, length=DEFAULT_LINE_LENGTH):
        self.write_separator(length=length, char=DEFAULT_LINE_BOLD_CHAR)

    def write_light_separator(self, length=DEFAULT_LINE_LENGTH):
        self.write_separator(length=length, char=DEFAULT_LINE_LIGHT_CHAR)

    def __str__(self):
        return self.msg
