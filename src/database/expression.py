import re

from sqlalchemy.sql.expression import BinaryExpression

SQLITE_REGEX_FUNCTIONS = {
    '=~':  ('REGEXP',   lambda value, regex: bool(re.match(regex, value))),
    '=~i': ('IREGEXP',  lambda value, regex: bool(re.match(regex, value, re.IGNORECASE))),
    '!~':  ('NREGEXP',  lambda value, regex: not re.match(regex, value)),
    '!~i': ('NIREGEXP', lambda value, regex: not re.match(regex, value, re.IGNORECASE)),
}

class RegexMatchExpression(BinaryExpression):
    pass


