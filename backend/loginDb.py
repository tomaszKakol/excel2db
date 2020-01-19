# -*- coding: utf-8 -*-
import os
import sys
from backend import labels
from peewee import *

_db_path = os.path.abspath('../%s' % (labels.DB_FILE_CREDENTIALS,))
db = SqliteDatabase(_db_path)
# db = SqliteDatabase(labels.DB_FILE_CREDENTIALS)

class BaseModel(Model):  # klasa bazowa
    class Meta:
        database = db


class Persons(BaseModel):
    login = CharField(null=False, unique=True)
    password = CharField()
    class Meta:
        order_by = (labels.LOGIN,)


def cnn():
    db.connect()  # nawiązujemy połączenie z bazą
    version = float(".".join(map(str, sys.version_info[:2])))
    print(version)
    if version < 3.7:
        db.create_tables(models=[Persons]) # tworzymy tabele
    else:
        db.create_tables(models=[Persons], options=True)  # tworzymy tabele
    return True


def addClient(login, password):
    try:
        persons, created = Persons.get_or_create(login=login, password=password)
        return persons
    except IntegrityError:
        return None







