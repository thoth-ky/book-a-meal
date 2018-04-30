'''model for Orders'''
from . import BaseModel


class Order(BaseModel):
    '''class for orders'''
    def __init__(self, order_id, username, meal, quantity=1,):
        self.meal_id = meal
        self.quantity = quantity
        self.order_id = order_id
        self.order_by = username
