'''model for Admin users'''

from .user import User


class Admin(User):
    '''Class for admin/caterer objects'''
    def __init__(self, username, email, password, admin=True):
        User.__init__(self, username=username, email=email, password=password)
        self.admin = admin
