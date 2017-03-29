from sqlalchemy                import String as ORM_String
from sqlalchemy.sql.expression import literal
from sqlalchemy.sql.operators  import custom_op

from .expression import RegexMatchExpression

class String(ORM_String):
    class comparator_factory(ORM_String.comparator_factory):
        def regexp(self, other):
            print("EXECUTOU")
            return RegexMatchExpression(self.expr, literal(other), custom_op('=~'))


        def iregexp(self, other):
            return RegexMatchExpression(self.expr, literal(other), custom_op('=~i'))


        def nregexp(self, other):
            return RegexMatchExpression(self.expr, literal(other), custom_op('!~'))


        def niregexp(self, other):
            return RegexMatchExpression(self.expr, literal(other), custom_op('!~i'))


