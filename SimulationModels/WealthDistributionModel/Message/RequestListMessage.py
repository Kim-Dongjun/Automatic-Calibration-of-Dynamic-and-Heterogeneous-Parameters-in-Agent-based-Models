
class RequestListMessage:

    def __init__(self,strHouseID,dblValue):

        self.strHouseID = strHouseID
        self.dblValue = dblValue

    def __str__(self):
        return "<"+self.strHouseID+":"+str(self.dblValue)+">"
