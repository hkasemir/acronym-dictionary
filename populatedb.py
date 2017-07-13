from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Definition

engine = create_engine('sqlite:///dictionary.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# user1
user1 = User(username='hkasemir')

session.add(user1)
session.commit()

