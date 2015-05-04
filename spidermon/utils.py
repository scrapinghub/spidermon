DEFAULT_LINE_LENGTH = 70
DEFAULT_LINE_CHAR = '-'


def line(length=DEFAULT_LINE_LENGTH, char=DEFAULT_LINE_CHAR):
    return char*length


def line_title(title, length=DEFAULT_LINE_LENGTH, char=DEFAULT_LINE_CHAR):
    title_length = len(title)+2
    left_length = (length-title_length)/2
    right_length = left_length + length - title_length - left_length * 2
    return '%s %s %s' % (char*left_length, title, char*right_length)
