"""Describe the language syntax."""

import re


class Symbol:
    """Describes the language symbols."""

    # General pattern of formulas
    pattern = '([a-z0-9&\-\|><\(\)]*)'
    accepted_chars = '([a-z0-9&\-\|><\(\)]*)'

    def __init__(self, value):
        """Init a propositional symbol."""
        self.value = value

    @classmethod
    def evaluate(cls, symbol):
        """Check if the given arg is a symbol."""
        regexp = re.compile(r'^%s$' % cls.pattern)
        return regexp.match(symbol)

    @classmethod
    def accepts_initial_char(cls, char):
        """Check if the operator accepts the given char as initial char."""
        regexp = re.compile(r'^%s$' % cls.accepted_initial_char)
        return regexp.match(char)

    def is_a(self, cls):
        """Check if this token is a given type."""
        return isinstance(self, cls)


class PropositionalSymbol(Symbol):
    """
    Describes the propositional symbols of the language.

    The propositional symbols are represented by any
    lowercase letter, followed or not by an integer index.

    Examples:
        p, p1, q23, r1890
    """

    accepted_initial_char = '[a-z]'
    pattern = '([a-z]{1}[0-9]*)'

    def subformulas(self):
        """
        Get the formula subformulas.

        Return itself as it is a propositional symbol.
        """
        return [self]

    def str_representation(self):
        """String representation of the symbol."""
        return self.value


class PontuationSymbol(Symbol):
    """
    Describes the pontuation symbols of the language.

    The pontuation symbols are represented by the
    opening and closing parenthesis.
    """

    pattern = '([\(\)])'


class OpeningParenthesis(PontuationSymbol):
    """Describes the opening parenthesis."""

    accepted_initial_char = '\('
    pattern = '\('


class ClosingParenthesis(PontuationSymbol):
    """Describes the closing parenthesis."""

    accepted_initial_char = '\)'
    pattern = '\)'


class Operator(Symbol):
    """Base class for language operators."""

    class Associativity:
        """Possible operators associativity."""

        LEFT = 1
        RIGHT = 0

    def subformulas(self):
        """Get the formula subformulas."""
        raise NotImplementedError


class BinaryOperator(Operator):
    """Describe binary operators."""

    def set_args(self, arg1, arg2):
        """Set the operator args."""
        self.arg1 = arg1
        self.arg2 = arg2

    def subformulas(self):
        """
        Get the formula subformulas.

        Return itself and the subformulas of its first and second args.
        """
        return [self] + self.arg1.subformulas() + self.arg2.subformulas()

    def str_representation(self):
        """String representation of the formula."""
        if self.arg1.is_a(PropositionalSymbol) or (
            self.arg1.is_a(Operator) and
            self.precendence <= self.arg1.precendence
        ):
            # In this case do not need parenthesis
            arg1_repr = self.arg1.str_representation()
        else:
            arg1_repr = '(' + self.arg1.str_representation() + ')'

        if self.arg2.is_a(PropositionalSymbol) or (
            self.arg2.is_a(Operator) and
            self.precendence <= self.arg2.precendence
        ):
            arg2_repr = self.arg2.str_representation()
        else:
            arg2_repr = '(' + self.arg2.str_representation() + ')'

        return arg1_repr + self.SYMBOL + arg2_repr


class UnaryOperator(Operator):
    """Describe unary operators."""

    def set_arg(self, arg):
        """Set the operator arg."""
        self.arg1 = arg

    def subformulas(self):
        """
        Get the formula subformulas.

        Return itself and the subformulas of its arg.
        """
        return [self] + self.arg1.subformulas()

    def str_representation(self):
        """String representation of the formula."""
        if self.arg1.is_a(PropositionalSymbol):
            return self.SYMBOL + self.arg1.str_representation()
        else:
            return self.SYMBOL + '(' + self.arg1.str_representation() + ')'


class Negation(UnaryOperator):
    """Describe the negation operator."""

    SYMBOL = '-'
    accepted_initial_char = '\-'
    pattern = '\-'

    precendence = 6
    associativity = Operator.Associativity.RIGHT


class Conjunction(BinaryOperator):
    """Describe the conjunction operator."""

    SYMBOL = '&'
    accepted_initial_char = '&'
    pattern = '&'

    precendence = 5
    associativity = Operator.Associativity.LEFT


class Disjunction(BinaryOperator):
    """Describe the disjunction operator."""

    SYMBOL = '|'
    accepted_initial_char = '\|'
    pattern = '\|'

    precendence = 4
    associativity = Operator.Associativity.LEFT


class Implication(BinaryOperator):
    """Describe the implication operator."""

    SYMBOL = '->'
    accepted_initial_char = '\-'
    pattern = '\->'

    precendence = 3
    associativity = Operator.Associativity.LEFT


class BiImplication(BinaryOperator):
    """Describe the bi-implication operator."""

    SYMBOL = '<->'
    accepted_initial_char = '<'
    pattern = '<\->'

    precendence = 2
    associativity = Operator.Associativity.LEFT
