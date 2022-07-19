import re
from numpy import mat
from soupsieve import match


absence_after_q = re.compile(
    r'After \{\S+\}, it is never the case that \{\S+\} \[holds\]\.')

bounded_absence_after_q = re.compile(
    r'After \{\S+\}, it is never the case that \{\S+\} \[holds\] within \S+ time units\.')

absence_before_r = re.compile(
    r'Before \{\S+\}, it is never the case that \{\S+\} \[holds\]\.')

bounded_absence_before_r = re.compile(
    r'Before \{\S+\}, it is never the case that \{\S+\} \[holds\] within \S+ time units\.')

absence_between_q_and_r = re.compile(
    r'Between \{\S+\} and \{\S+\}, it is never the case that \{\S+\} \[holds\]\.')

bounded_absence_between_q_and_r = re.compile(
    r'Between \{\S+\} and \{\S+\}, it is never the case that \{\S+\} \[holds\] between \S+ and \S+ time units\.')

universality_after_q = re.compile(
    r'After \{\S+\}, it is always the case that \{.+\} \[holds\]\.')

bounded_universality_after_q = re.compile(
    r'After \{\S+\}, it is always the case that \{.+\} \[holds\] within \S+ time units\.')

universality_before_r = re.compile(
    r'Before \{\S+\}, it is always the case that \{\S+\} \[holds\]\.')

bounded_universality_before_r = re.compile(
    r'Before \{\S+\}, it is always the case that \{\S+\} \[holds\] within \S+ time units\.')

bounded_universality_between_q_and_r = re.compile(
    r'Between \{\S+\} and \{\S+\}, it is always the case that \{\S+\} \[holds\] between \S+ and \S+ time units\.')

bounded_recurrence_globally = re.compile(
    r'Globally, \{\S+\} \[holds\] repeatedly every \S+ time units\.')

bounded_recurrence_between_q_and_r = re.compile(
    r'Between \{\S+\} and \{\S+\}, \{\S+\} \[holds\] repeatedly every \S+ time units.')

bounded_response_globally = re.compile(
    r'Globally, if \{\S+\} \[has occurred\] then in response \{\S+\} \[eventually holds\] between \S+ and \S+ time units.')

bounded_response_between_q_and_r = re.compile(
    r'Between \{\S+\} and \{\S+\}, if \{\S+\} \[has occurred\] then in response \{\S+\} \[eventually holds\] between \S+ and \S+ time units.')
