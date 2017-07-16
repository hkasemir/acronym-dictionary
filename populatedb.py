from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Definition

engine = create_engine('sqlite:///dictionary.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


user1 = User(username='testuser')


session.add(user1)
session.commit()

category1 = Category(name='slang')
session.add(category1)
session.commit()

word1= Definition(word='LOL', definition='Laugh out loud',
        created_by=user1.username,
        category_name=category1.name
        )
session.add(word1)
session.commit()

all_users = session.query(User).all()
all_categories = session.query(Category).all()
all_words = session.query(Definition).all()

for u in all_users:
    print u.username

for c in all_categories:
    print c.name

for w in all_words:
    print w.word

# Base.metadata.drop_all(engine)

