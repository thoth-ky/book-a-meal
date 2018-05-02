class ItemAlreadyExists(Exception):
    '''Exception when an object already exists'''
    pass


class UnknownClass(Exception):
    '''Exception for unknown or unexpectd datatypes'''
    pass


class BaseModel:
    '''Base model to be inherited  by other modells'''
    def make_dict(self):
        '''serialize class'''
        return self.__dict__

    def update(self, new_data):
        '''new_data is a dictionary containing new info'''
        current_data = self.make_dict()
        data_keys = current_data.keys()
        new_keys = new_data.keys()
        for key in data_keys:
            for new_data_key in new_keys:
                if key == new_data_key:
                    current_data[key] = new_data[new_data_key]
