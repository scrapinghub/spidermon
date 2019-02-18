from six import PY2

SYNTAXERROR_EXPRESSIONS = ["?", "a string", "a="]

INVALID_EXPRESSIONS = [
    None,
    0,
    "",
    """
    """,
    "a > b\na > b",
    "import os",
    "from os import *",
    "for i in range(10): pass",
    "def something(): pass",
    "lambda x: x",
    "del a",
    # "print(a)",
    "raise Exception",
    "pass",
    "return",
    "yield x",
    # Assignment Operations
    "a = 1",
    "a += 1",
    "a -= 1",
    "a *= 1",
    "a /= 1",
    "a %= 1",
    "a **= 1",
    "a //= 1",
]

VALID_EXPRESSIONS = [
    # Strings
    "'single quoted string'",
    '"double quoted string"',
    "u'unicode single quoted string'",
    'u"unicode double quoted string"',
    # Numbers
    "0",
    ".5",
    "-10",
    "10",
    "1.0",
    "-1.0",
    "3.14j",
    # Sequences
    "[1, 2, 3]",
    "{'a': 1, 'b': 1}",
    "set()",
    "(1, 2)",
    "len(a)",
    # Constants
    "None",
    "True",
    "False",
    # Arithmetic Operations
    "-a",
    "a + 1",
    "a - 1",
    "a / 1",
    "a * 1",
    "a % 1",
    "a ** 1",
    "a // 1",
    # Comparison Operations
    "a == b",
    "a != b",
    "a > b",
    "a < b",
    "a >= b",
    "a <= b",
    "1 < a < 10",
    # Bitwise Operations
    "a & b",
    "a | b",
    "a ^ b",
    "~a",
    "a << b",
    "a >> b",
    # Logical Operations
    "a and b",
    "a or b",
    "not a",
    # Membership Operations
    "a in b",
    "a not in b",
    # Identity Operations
    "a is 10",
    "a is not 10",
    # Inline if statement
    "a if b else c",
    # Subscripting
    "a[1]",
    "a[1:2]",
    "a[1:2, 3]",
    # Comprehensions
    "[i for i in range(10)]",
    "{i: i**2 for i in range(10)}",
    "{i for i in range(10)}",
    "[n for n in range(10) if n>5]",
    # Attribute access
    "stats.scraped_items",
]


EXPRESSIONS_TO_EVALUATE = [
    ("stats.item_scraped_count == 10000", False),
    ("stats.item_scraped_count != 10000", True),
    ("stats.item_scraped_count < 10000", False),
    ("stats.item_scraped_count > 10000", True),
    ("stats.item_scraped_count <= 10000", False),
    ("stats.item_scraped_count >= 10000", True),
    ("10000 < stats.item_scraped_count < 100000", True),
    ("stats.item_scraped_count == .5", False),
    ("stats.item_scraped_count < .5", False),
    ("stats.item_scraped_count > .5", True),
    ('stats.finish_reason in ["finished"]', True),
    ('stats.finish_reason in ["a", "b"]', False),
    ('stats.finish_reason not in ["a", "b"]', True),
    ('stats.finish_reason in {"finished": 0}', True),
    ('stats.finish_reason in {"finished": 0}.keys()', True),
    ('stats.finish_reason in ("finished",)', True),
    ('len(stats.finish_reason) == len("finished")', True),
    ("stats.finish_reason is not None", True),
    ("len(stats.finish_reason) > 0", True),
    ("(len(stats.finish_reason) > 0) == True", True),
    ("(len(stats.finish_reason) > 0) != False", True),
    ("(len(stats.finish_reason) > 0) is not False", True),
    ("(len(stats.finish_reason) > 0) is True", True),
    ('stats["downloader/exception_count"] == 16', True),
    ('-stats["downloader/exception_count"] == -16', True),
    ('stats["downloader/exception_count"]+1 == 17', True),
    ('stats["downloader/exception_count"]-1 == 15', True),
    ('stats["downloader/exception_count"]/2 == 8', True),
    ('stats["downloader/exception_count"]*2 == 32', True),
    ('stats["downloader/exception_count"]%3 == 1', True),
    ('stats["downloader/exception_count"]**2 == 256', True),
    ('stats["downloader/exception_count"]//2 == 8', True),
    ('stats["downloader/exception_count"]*2/2 == 16', True),
    ("stats.has_errors and stats.has_redirections", True),
    ("stats.has_errors or stats.has_redirections", True),
    ("not stats.has_errors", False),
    ("stats.has_errors is True", True),
    ("stats.has_errors is not True", False),
    ("True if stats.has_errors else False", True),
    ("True if not stats.has_errors else False", False),
    ("stats.item_scraped_count in range(29830, 29840)", True),
]


if PY2:
    VALID_EXPRESSIONS.extend(["51924361L", "a <> b"])
    EXPRESSIONS_TO_EVALUATE.extend([("stats.item_scraped_count <> 10000", True)])
