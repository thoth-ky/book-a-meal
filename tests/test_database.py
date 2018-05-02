'''Tests for database'''
from datetime import datetime
from . import BaseTestClass


class TestDatabase(BaseTestClass):
    '''Test database models'''
    def test_can_add_user(self):
        '''test users can be added to db'''
        user = self.user_model(
            username='joe', email='j@ma.com', password='test1234')
        user.save()
        q_user = self.user_model.query.filter_by(username='joe').first()
        self.assertEqual(user, q_user)

    def test_user_can_be_promoted(self):
        user = self.create_user()
        self.assertEqual(user.admin, False)
        self.user_model.promote_user(user)
        self.assertEqual(user.admin, True)

    def test_password_validation(self):
        user = self.create_user()
        self.assertFalse(user.validate_password('wrongpass'))
        self.assertTrue(user.validate_password(password=self.test_user['password']))

    def test_token_creation_and_decoding(self):
        user = self.create_user()
        token = user.generate_token()
        username = self.user_model.decode_token(token)
        self.assertEqual(username, user.username)

    def test_can_add_meal(self):
        '''test meals can be added'''
        meal = self.meal_model(
            name='Fish', price=100, description='Tilapia')
        meal.save()
        q_meal = self.meal_model.query.filter_by(meal_id=meal.meal_id).first()
        self.assertEqual(meal, q_meal)

    def test_can_set_meal_to_available(self):
        meal = self.create_meal()
        meal.save()
        self.assertFalse(meal.available)
        meal.now_available()
        meal.save()
        meal = self.meal_model.query.filter_by(meal_id=meal.meal_id).first()
        self.assertTrue(meal.available)

    def test_can_update_meals(self):
        '''test meals can be updated'''
        meal = self.create_meal()
        meal.save()
        new_data = {'price': 400}
        e = meal.update(new_data=new_data)
        self.assertNotEqual(e, 'Field not valid.')
        self.assertEqual(meal.price, new_data['price'])

    def test_can_delete_meals(self):
        meal = self.create_meal()
        meal.save()
        q_meal = self.meal_model.query.filter_by(meal_id=meal.meal_id).first()
        self.assertNotEqual(q_meal, None)
        meal.delete()
        q_meal = self.meal_model.query.filter_by(meal_id=meal.meal_id).first()
        self.assertEqual(q_meal, None)

    def test_can_make_orders(self):
        '''test users can store orders'''
        meal = self.create_meal()
        user = self.create_user()
        order_id = self.order_model.generate_order_id()
        order = self.order_model(order_id=order_id, meal=meal, user_id=user.user_id, quantity=2)
        order.save()
        self.assertEqual(order.owner.username, user.username)
        self.assertEqual(meal.name, order.meal.name)
        self.assertEqual(order.quantity, 2)

    def test_can_store_menu(self):
        '''test DB can hold menu'''
        self.meal1.save()
        self.meal2.save()
        self.meal1.now_available()
        self.meal2.now_available()
        self.menu.save()
        self.menu.add_meal(self.meal1)
        self.menu.save()
        menu = self.menu_model.query.filter_by(id=1).first()
        self.assertTrue(isinstance(menu.meals, list))
        self.assertTrue(isinstance(menu.meals[0], self.meal_model))

    def test_user_can_order_several_meals(self):
        self.meal1.save()
        self.meal2.save()
        user = self.create_user()
        order_id = self.order_model.generate_order_id()
        order1 = self.order_model(order_id=order_id, meal=self.meal1, user_id=user.user_id)
        order2 = self.order_model(order_id=order_id, meal=self.meal2, user_id=user.user_id, quantity=4)
        order1.save()
        order2.save()
        self.assertTrue(isinstance(order1.owner, self.user_model))
        self.assertTrue(isinstance(order1.meal, self.meal_model))
        self.assertTrue(isinstance(order2.owner, self.user_model))
        self.assertTrue(isinstance(order2.meal, self.meal_model))

    def test_cant_edit_order_after_given_time(self):
        pass
