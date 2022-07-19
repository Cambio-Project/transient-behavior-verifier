from numpy import var


class Predicates:
    """A class containing the predicate functions"""

    def __init__(self, value=None):
        self.value = value
        self.trendLast = None

    def equal(self, variable):
        return variable == self.value

    def notEqual(self, variable):
        return variable != self.value

    def bigger(self, variable):
        return variable > self.value

    def biggerEqual(self, variable):
        return variable >= self.value

    def smaller(self, variable):
        return variable < self.value

    def smallerEqual(self, variable):
        return variable <= self.value

    def boolean(self, boolean_value):
        return boolean_value

    def trendUpward(self, variable):
        if(self.trendLast is None):
            self.trendLast = variable
            return False
        else:
            if(self.trendLast <= variable):
                self.trendLast = variable
                return True
            else:
                self.trendLast = variable
                return False

    def trendUpwardStrict(self, variable):
        if(self.trendLast is None):
            self.trendLast = variable
            return False
        else:
            if(self.trendLast < variable):
                self.trendLast = variable
                return True
            else:
                self.trendLast = variable
                return False

    def trendDownward(self, variable):
        if(self.trendLast is None):
            self.trendLast = variable
            return False
        else:
            if(self.trendLast >= variable):
                self.trendLast = variable
                return True
            else:
                self.trendLast = variable
                return False

    def trendDownwardStrict(self, variable):
        if(self.trendLast is None):
            self.trendLast = variable
            return False
        else:
            if(self.trendLast > variable):
                self.trendLast = variable
                return True
            else:
                self.trendLast = variable
                return False
