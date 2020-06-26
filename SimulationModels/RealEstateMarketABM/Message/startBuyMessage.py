class startBuyMessage:

    def __init__(self, currentTime):
        self.currentTime = currentTime

    def __str__(self):
        return "<Start Buy process of time "+str(self.currentTime)+">"