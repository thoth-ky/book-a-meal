'''model for Menus'''
from datetime import datetime

# local imports
from . import BaseModel

TODAY = datetime.utcnow().date()


class Menu(BaseModel):
    '''model for Menus'''
    def __init__(self, meals, date=TODAY):
        self.meals = meals
        self.date = str(date)
