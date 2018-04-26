'''Tests for database'''
from datetime import datetime
from . import BaseTestClass, Database


class TestDatabase(BaseTestClass):
    def test_can_add_user(self):
        user = self.user_model(
            username='john', email='j@ma.com', password='test1234')
        self.database.add(user)
        self.assertEqual(
            user, self.database.users['john'])

    def test_can_add_meal(self):
        meal = self.meal_model(
            meal_id=1, name='Fish', price=100, description='Tilapia')
        self.database.add(meal)
        self.assertEqual(
            meal, self.database.meals['1'])

    def test_can_update_meals(self):
        self.create_meal()
        new_data = {'price': 400}
        meal = self.database.meals['1']
        meal.update(new_data)
        self.assertEqual(meal.price, new_data['price'])

    def test_can_store_orders(self):
        self.create_meal()
        meal = [self.database.meals['1']]
        order = self.order_model(meal=meal, order_id=1, username='joe')
        self.database.add(order)
        self.assertEqual(order, self.database.orders['1'])

    def test_can_store_menu(self):
        self.create_meal()
        menu_list = [self.database.meals['1']]
        menu = self.menu_model(menu_list)
        self.database.add(menu)
        self.assertEqual(menu, self.database.current_menu[str(datetime.utcnow().date())])

    def test_adding_unrecognized_type(self):
        string = 'this is not a model class object'
        err = self.database.add(string)
        expected = 'Unknown type'
        self.assertEqual(expected, err)
