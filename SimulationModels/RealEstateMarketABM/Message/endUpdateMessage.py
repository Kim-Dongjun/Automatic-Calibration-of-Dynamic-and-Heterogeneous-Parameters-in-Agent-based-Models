class endUpdateMessage:

    def __init__(self, strID):
        self.strID = strID

    def __str__(self):
        return "<" + self.strID + " finished Update process >"