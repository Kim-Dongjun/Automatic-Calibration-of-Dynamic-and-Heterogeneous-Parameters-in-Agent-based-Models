class decisionInfoMessage:

    def __init__(self, sender, decision, dealingType):
        self.sender = sender
        self.decision = decision
        self.dealingType = dealingType

    def __str__(self):
        return "< decision Message >"