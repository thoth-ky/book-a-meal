'''Tests for database'''
from . import BaseTestClass


class TestDatabase(BaseTestClass):
    def test_can_add_user(self):
        user = self.User(username='john', email='j@ma.com', password='test1234')
        self.Database.add(user)
        self.assertEqual(user, self.Database.users[0])

    def test_can_add_meal(self):
        meal = self.Meal(meal_id=1, name='Fish', price=100, description='Tilapia')
        self.Database.add(meal)
        self.assertEqual(meal, self.Database.meals[0])

    def test_can_update_meals(self):
        self.create_meal()
        new_data = {'price': 400}
        meal = self.Database.meals['1']
        meal.update(new_data)
        self.assertEqual(meal['price'], new_data['price'])

    def test_can_store_orders(self):
        self.create_meal()
        meals_list = [self.Database.meals[0]]
        order = self.Order(meals=meals_list)
        self.Database.add(order)
        self.assertEqual(order, self.Database.orders[0])

    def test_can_store_menu(self):
        self.create_meal()
        menu_list = [self.Database.meals[0]]
        menu = self.Menu(menu_list)
        self.Database.add(menu)
        self.assertEqual(menu, self.Database.current_menu[0])

    def test_adding_unrecognized_type(self):
        string = 'this is not a model class object'
        err = self.Database.add(string)
        expected = 'Unknown type'
        self.assertEqual(expected, err)
