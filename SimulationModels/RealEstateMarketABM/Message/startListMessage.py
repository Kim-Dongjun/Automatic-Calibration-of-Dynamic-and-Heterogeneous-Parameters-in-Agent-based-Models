class startListMessage:

    def __init__(self, currentTime):
        self.currentTime = currentTime

    def __str__(self):
        return "<Start List process of time "+str(self.currentTime)+">"