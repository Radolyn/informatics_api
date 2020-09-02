from enum import Enum


class UserType(Enum):
    school = 1
    student = 2
    teacher = 3


class User(object):
    def __init__(self, id, first_name='', last_name='', email='', country='', city='', type=''):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.country = country
        self.city = city
        self.type: UserType = type
        self.school = 'Не указано'
        self.grade = 0
        self.graduate_year = 1980
