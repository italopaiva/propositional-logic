"""Describe the possible operations."""

from lp.interpreter import Interpreter, TruthTable, SetTruthTable


class Operation:
    """Base class for operations."""

    def perform(self, *args):
        """Perform the operation."""
        raise NotImplementedError

    def parse(self, line):
        """
        Generic parser for operations.

        A line generally comes like that:

            OPERATION, formula1, formula2, ...

        So it returns the comma separated values without the operation as list.
        """
        args = line.split(',')
        return args[1:]


class SemanticStatus(Operation):
    """Verify the semantic status of a formula."""

    SYMBOL = 'S'

    def perform(self, formula):
        """Check a formula semantic status."""
        truth_table = TruthTable(formula)
        valuations = truth_table.get_formula_valuations()

        formula_values = []
        for line, valuation in valuations.items():
            formula_values.append(valuation[1])

        status = self.check_status(formula_values)

        return '[%s, [%s]]' % (status, truth_table.str_representation())

    def check_status(self, formula_values):
        """Get the formulas semantic status based on its valuations."""
        tautology = True in formula_values and False not in formula_values
        contradiction = False in formula_values and True not in formula_values

        if tautology:
            status = "TAUTOLOGIA"
        elif contradiction:
            status = "CONTRADICAO"
        else:
            status = "CONTINGENCIA"

        return status


class SemanticEquivalence(Operation):
    """Verify if two formulas are semantic equivalent."""

    SYMBOL = 'EQ'

    def perform(self, formula1, formula2):
        """Check if the two formulas are equivalent."""
        quid_pro_quo, truth_table = self.check_equivalence(formula1, formula2)
        equivalent = 'SIM' if quid_pro_quo else 'NAO'

        return '[%s, [%s]]' % (
            equivalent,
            truth_table.str_representation()
        )

    def check_equivalence(self, formula1, formula2):
        """."""
        truth_table = SetTruthTable([formula1, formula2])

        formula1 = Interpreter.parse_expression(formula1)
        formula2 = Interpreter.parse_expression(formula2)

        models1 = truth_table.get_formula_models(formula1.str_representation())
        models2 = truth_table.get_formula_models(formula2.str_representation())

        equivalent = True
        for valuation_index, valuation in models1.items():
            if valuation_index not in models2:
                equivalent = False
                break

        if equivalent:
            # Check if the second formula models are in the first formula
            for valuation_index, valuation in models2.items():
                if valuation_index not in models1:
                    equivalent = False
                    break

        return equivalent, truth_table


class Consistency(Operation):
    """Verify if a set of formulas is consistent."""

    SYMBOL = 'C'

    def perform(self, formulas):
        """Check if the set of formulas is consistent."""
        truth_table = SetTruthTable(formulas)
        formulas_models = truth_table.get_formulas_set_models()

        consistent = 'SIM' if formulas_models else 'NAO'

        return '[%s, [%s]]' % (
            consistent,
            truth_table.str_representation()
        )

    def parse(self, line):
        """Parse a bracketed, comma separated formulas into a list."""
        # Remove the operation symbol from the line
        line = line.replace(self.SYMBOL, '')
        # Remove the whitespaces and the first character (that will be a comma)
        line = "".join(line.split())[1:]
        # Remove the brackets of the string
        line = line.replace('[', '').replace(']', '')
        # Split the line on comma to get all formulas of the set as list
        args = line.split(',')
        return [args]


class LogicConsequence(Operation):
    """Verify if a formula is logic consequence of a set of formulas."""

    SYMBOL = 'CL'

    def perform(self, formulas_set, formula):
        """Check if the formula is logic consequence of the formulas_set."""
        if '' in formulas_set and len(formulas_set) is 1:
            return self.is_logic_consequence_of_empty_set(formula)

        truth_table = SetTruthTable(formulas_set + [formula])
        formula = Interpreter.parse_expression(formula)

        formulas = {}
        for f in formulas_set:
            form = Interpreter.parse_expression(f)
            formulas[form.str_representation()] = form

        set_models = truth_table.get_formulas_set_models(formulas)
        formula_models = truth_table.get_formula_models(
            formula.str_representation()
        )

        logic_consequence = True
        for valuation_index, valuation in set_models.items():
            if valuation_index not in formula_models:
                logic_consequence = False
                break

        consequence = 'SIM' if logic_consequence else 'NAO'

        return '[%s, [%s]]' % (
            consequence,
            truth_table.str_representation()
        )

    def is_logic_consequence_of_empty_set(self, formula):
        """Check if a formula is logic consequence of the empty set."""
        truth_table = TruthTable(formula)
        valuations = truth_table.get_formula_valuations()

        logic_consequence = True
        for valuation_index, valuation in valuations.items():
            if valuation[1] is False:
                logic_consequence = False
                break

        consequence = 'SIM' if logic_consequence else 'NAO'

        return '[%s, [%s]]' % (
            consequence,
            truth_table.str_representation()
        )

    def parse(self, line):
        """Parse a bracketed, comma separated formulas into a list."""
        # Remove the operation symbol from the line
        line = line.replace(self.SYMBOL, '')
        # Remove the whitespaces and the first character (that will be a comma)
        line = "".join(line.split())[1:]
        # Remove the brackets of the string
        line = line.replace('[', '').replace(']', '')
        # Split the line on comma to get all formulas of the set as list
        args = line.split(',')
        # The set of formulas will be all the elements but the last one
        formulas_set = args[:-1]
        # The formula will be the last element in the list
        formula = args[-1]
        return [formulas_set, formula]
