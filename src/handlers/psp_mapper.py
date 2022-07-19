import re
from numpy import mat
from soupsieve import match
from handlers.psp_patterns import *


class PSPMapper():
    """A class responsible for the mapping of PSPs to past-MTL formulas"""

    # maps a pattern regex to the past-MTL formula
    def map_pattern(input_pattern):

        list_predicates = re.findall('\{\S+\}|\{.+\}|\d+', input_pattern)
        list_predicates_cleaned = []
        for item in list_predicates:
            item = item.replace("{", "")
            item = item.replace("}", "")
            list_predicates_cleaned.append(item)
        list_predicates = list_predicates_cleaned

        output = None
        if(re.match(absence_after_q, input_pattern)):
            output = "always((once("+list_predicates[0]+")) -> ((not " + \
                list_predicates[1]+") since "+list_predicates[0]+"))"

        elif(re.match(bounded_absence_after_q, input_pattern)):
            output = "always((once[0," + list_predicates[2] + "]("+list_predicates[0]+")) -> ((not " + \
                list_predicates[1]+") since "+list_predicates[0]+"))"

        elif(re.match(absence_before_r, input_pattern)):
            output = "always(" + list_predicates[0] + \
                "->(always(not "+list_predicates[1]+")))"

        elif(re.match(bounded_absence_before_r, input_pattern)):
            output = "always(" + list_predicates[0] + \
                "->(always[0," + list_predicates[2] + \
                "](not "+list_predicates[1]+")))"

        elif(re.match(absence_between_q_and_r, input_pattern)):
            output = "always("+list_predicates[1]+" && not("+list_predicates[0]+") && once(" + \
                list_predicates[0]+"))->((not "+list_predicates[2] + \
                ") since "+list_predicates[0]+")"

        elif(re.match(bounded_absence_between_q_and_r, input_pattern)):
            output = "always("+list_predicates[1]+" && !"+list_predicates[0]+" && once " + \
                list_predicates[0]+")->((not "+list_predicates[2] + \
                ") since["+list_predicates[3]+"," + \
                list_predicates[4]+"] "+list_predicates[0]+")"

        elif(re.match(universality_after_q, input_pattern)):
            print(list_predicates)
            output = "always((once("+list_predicates[0]+")) -> (" + \
                list_predicates[1]+" since "+list_predicates[0]+"))"

        elif(re.match(bounded_universality_after_q, input_pattern)):
            output = "always((once[0," + list_predicates[2] + "]("+list_predicates[0]+")) -> (" + \
                list_predicates[1]+" since "+list_predicates[0]+"))"

        elif(re.match(universality_before_r, input_pattern)):
            output = "always(" + list_predicates[0] + \
                "->(always("+list_predicates[1]+")))"

        elif(re.match(bounded_universality_before_r, input_pattern)):
            output = "always(" + list_predicates[0] + \
                "->(always[0,"+list_predicates[2]+"]("+list_predicates[1]+")))"

        elif(re.match(bounded_universality_between_q_and_r, input_pattern)):
            output = "always("+list_predicates[1]+" && !"+list_predicates[0]+" && once " + \
                list_predicates[0]+")->("+list_predicates[2] + \
                " since["+list_predicates[3]+"," + \
                list_predicates[4]+"] "+list_predicates[0]+")"

        elif(re.match(bounded_recurrence_globally, input_pattern)):
            output = "always(once[0,"+list_predicates[1] + \
                "]("+list_predicates[0]+"))"

        elif(re.match(bounded_recurrence_between_q_and_r, input_pattern)):
            output = "always(("+list_predicates[1]+" && !"+list_predicates[0]+" && once "+list_predicates[0]+") -> ((once[0," + \
                list_predicates[3]+"]("+list_predicates[2]+" or " + \
                list_predicates[0]+")) since "+list_predicates[0]+"))"

        elif(re.match(bounded_response_globally, input_pattern)):
            output = "always(("+list_predicates[1]+" -> once["+list_predicates[2]+","+list_predicates[3]+"] "+list_predicates[0] + \
                ") and not( not("+list_predicates[1]+") since[" + \
                list_predicates[3]+",inf] "+list_predicates[0]+"))"

        elif(re.match(bounded_response_between_q_and_r, input_pattern)):
            output = "always(("+list_predicates[1]+" && " + "!"+list_predicates[0] + " && once " + \
                list_predicates[0]+") -> ( (("+list_predicates[3] + \
                " -> once[" + list_predicates[4] + ","+list_predicates[5]+"] "+list_predicates[2] + \
                ") and not( not("+list_predicates[3]+") since["+list_predicates[5] + \
                ",inf] "+list_predicates[2]+")) since "+list_predicates[0]+"))"

        else:
            print("Pattern could not be matched!")
            raise Exception("PSP pattern could not be matched!")

        print("MTL Formula:", output)
        return output
