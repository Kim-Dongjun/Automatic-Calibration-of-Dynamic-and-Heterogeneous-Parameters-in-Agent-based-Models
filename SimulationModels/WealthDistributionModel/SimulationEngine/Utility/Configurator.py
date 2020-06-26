
class Configurator:
    def __init__(self):
        self.objConfiguration = {}

    def addConfiguration(self,objKey,objValue):
        self.objConfiguration[objKey] = objValue

    def getConfiguration(self,objKey):
        if objKey in self.objConfiguration.keys():
            #print("!!! " + str(self.objConfiguration[objKey]))
            return self.objConfiguration[objKey]
        else:
            return None

    def __str__(self):
        return str(self.objConfiguration)