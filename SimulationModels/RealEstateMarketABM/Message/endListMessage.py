class endListMessage:

    def __init__(self, strID):
        self.strID = strID

    def __str__(self):
        return "<" + self.strID + " finished List process >"