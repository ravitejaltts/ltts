import random

class SampleNumberService:    
    @staticmethod
    def addTwo(n):
        return n + 2
    
    @staticmethod
    def addRandom(n):
        return n + random.randrange(1,10)

class GroceryListItem:
    def __init__(self, grocery, quantity):
        self.grocery = grocery
        self.quantity = quantity
        self.purchased = False

    def purchase(self):
        self.purchased = True

