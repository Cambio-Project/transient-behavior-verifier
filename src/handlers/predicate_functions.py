from numpy import var


class Predicates:

    def __init__(self, value=None, limitVar=None):
        self.value = value
        self.limitVar = limitVar
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

    # new functions

    def trendUpward(self, variable):
        if(self.trendLast is None):
            self.trendLast = variable
            return True
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
            return True
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
            return True
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
            return True
        else:
            if(self.trendLast > variable):
                self.trendLast = variable
                return True
            else:
                self.trendLast = variable
                return False

    # def biggerDynamic(value1, value2):
    #     return value1 > value2

    # def smallerDynamic(value1, value2):
    #     return value1 > value2

    # def equalDynamic(value1, value2):
    #     return value1 > value2

    # make sure to make this is consistent
    # def interval(self, variable):
        # print(self.value,variable,self.limitVar,self.value < variable < self.limitVar)
        # return self.value < variable < self.limitVar
