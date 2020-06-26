class startUpdateMessage:

    def __init__(self, currentTime):
        self.currentTime = currentTime

    def __str__(self):
        return "<Start Update process of time "+str(self.currentTime)+">"