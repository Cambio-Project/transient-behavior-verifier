
from handlers.psp_mapper import FormulaMapper
from handlers.predicate_functions import Predicates


class FormulaHandler():

    def get_params_string(self, formula_info):
        param_counter = 0
        params_string = ""
        for predicate in formula_info["predicates_info"]:
            if (param_counter == 0):

                if ('boolean' in predicate['predicate_logic'] or 'trend' in predicate['predicate_logic']):
                    params_string = params_string + \
                                    predicate['predicate_name'] + '=' + \
                                    "predicate_functions.Predicates()." + \
                                    predicate['predicate_logic'] + ""

                else:
                    params_string = params_string + \
                                    predicate['predicate_name'] + '=' + \
                                    "predicate_functions.Predicates(" + predicate['predicate_comparison_value'] + \
                                    ")." + predicate['predicate_logic'] + ""
            else:

                if ('boolean' in predicate['predicate_logic'] or "trend" in predicate['predicate_logic']):
                    params_string = params_string + "," + \
                                    predicate['predicate_name'] + '=' + \
                                    "predicate_functions.Predicates()." + \
                                    predicate['predicate_logic'] + ""

                else:
                    params_string = params_string + "," + \
                                    predicate['predicate_name'] + '=' + \
                                    "predicate_functions.Predicates(" + \
                                    predicate['predicate_comparison_value'] + \
                                    ")." + predicate['predicate_logic'] + ""

            param_counter = param_counter + 1

        return params_string

    def handle_formula(self, formula_info):
        formula = formula_info['specification']
        if formula_info['specification_type'] == 'psp':
            formula = FormulaMapper.from_psp(formula).get_formula()
        if formula_info['specification_type'] == 'tbv':
            formula = FormulaMapper.from_tbv(formula).get_formula()
        params_string = self.get_params_string(formula_info)
        return formula, params_string
