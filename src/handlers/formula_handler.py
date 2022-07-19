
from handlers.psp_mapper import PSPMapper
from handlers.predicate_functions import Predicates


class FormulaHandler():

    def handle_formula(self, formula_info):
        formula = formula_info['specification']
        print("Specification:", formula)
        if(formula_info['specification_type'] == 'psp'):
            print(formula)
            formula = PSPMapper.map_pattern(formula)
        param_counter = 0
        params_string = ""
        print("Predicates:")
        for predicate in formula_info["predicates_info"]:
            print(predicate)
            if(param_counter == 0):

                if('boolean' in predicate['predicate_logic'] or 'trend' in predicate['predicate_logic']):
                    params_string = params_string + \
                        predicate['predicate_name']+'=' + \
                        "predicate_functions.Predicates()." + \
                        predicate['predicate_logic']+""

                else:
                    params_string = params_string + \
                        predicate['predicate_name']+'=' + \
                        "predicate_functions.Predicates("+predicate['predicate_comparison_value'] + \
                        ")."+predicate['predicate_logic']+""
            else:

                if('boolean' in predicate['predicate_logic'] or "trend" in predicate['predicate_logic']):
                    params_string = params_string+"," + \
                        predicate['predicate_name']+'=' + \
                        "predicate_functions.Predicates()." + \
                        predicate['predicate_logic']+""

                else:
                    params_string = params_string+"," + \
                        predicate['predicate_name']+'=' + \
                        "predicate_functions.Predicates(" + \
                        predicate['predicate_comparison_value'] + \
                        ")."+predicate['predicate_logic']+""

            param_counter = param_counter+1

        params_string = params_string+""

        # print("params ---", params_string)
        return formula, params_string
