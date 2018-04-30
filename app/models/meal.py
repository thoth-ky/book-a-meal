'''Model for Meal'''
from . import BaseModel


class Meal(BaseModel):
    '''Class to represent the Meal objects'''
    def __init__(self, meal_id, name, price, description):
        self.meal_id = meal_id
        self.name = name
        self.price = price
        self.description = description

    def __str__(self):
        '''String representation of objects'''
        return '<Meal: {}'.format(self.name)
