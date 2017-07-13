from flask import render_template, flash, jsonify
from models import Base, User, Definition, Category
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///dictionary.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def get_or_create_user(username, access_token):
    session = DBSession()
    user = session.query(User).filter_by(username=username)
    if not user:
        user = User(username = username)
        session.add(user)
        session.commit()
    user.update({User.token_hash: user.first().hash_token(access_token)})
    session.commit()
    return user.first()

def add_category(form):
    session = DBSession()
    session.add(Category(name=form['name']))
    session.commit()
    flash('menu item %s edited!' % form['name'])

def show_main():
    session = DBSession()
    categories = session.query(Category)
    return render_template('index.html', catgories=categories)

