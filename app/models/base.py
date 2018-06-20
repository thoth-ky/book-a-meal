'''Base models '''
from .. import DB


class BaseModel(DB.Model):
    '''Base model to be inherited  by other modells'''
    __abstract__ = True

    def make_dict(self):
        '''serialize class'''
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}

    def save(self):
        '''save object'''
        try:
            DB.session.add(self)
            DB.session.commit()
            return None
        except Exception as e:
            DB.session.rollback()
            return {
                'message': 'Save operation not successful',
                'error': str(e)
            }

    def delete(self):
        '''delete object'''
        try:
            DB.session.delete(self)
            DB.session.commit()
        except Exception as e:
            DB.session.rollback()
            return {
                'message': 'Delete operation failed',
                'error': str(e)
            }

    def update(self, new_data):
        '''new_data is a dictionary containing the field as key and new value
        as value'''
        for key in new_data.keys():
            self.put(key, new_data[key])

    def put(self, field, value):
        '''insert operation. field is the attribute name and value is the
        value being inseted, it can be a list or not. A list is used to
        populate a relationship field'''
        if isinstance(value, list):
            old_value = getattr(self, field)
            old_value.extend(value)
            self.save()
        else:
            setattr(self, field, value)
            self.save()

    @classmethod
    def has(cls,**kwargs):
        '''check if table contains record atching given kwargs'''
        obj = cls.query.filter_by(**kwargs).first()
        if isinstance(obj, cls):
            return True
        return False

    @classmethod
    def get(cls, **kwargs):
        '''get a record from table matching given kwarg'''
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def get_all(cls):
        '''return a list of all records in the table'''
        return cls.query.all()

