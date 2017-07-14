from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Definition

engine = create_engine('sqlite:///dictionary.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# user1
# user1 = session.query(User).filter(User.username=='hkasemir').one()
# 
# session.delete(user1)
# session.commit()

all_users = session.query(User).all()
all_categories = session.query(Category).all()

for u in all_users:
    print u.username

for c in all_categories:
    print c.name

