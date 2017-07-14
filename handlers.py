from flask import render_template, flash, jsonify
from models import Base, User, Definition, Category
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///dictionary.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

#### user ####

def get_or_create_user(username, access_token):
    session = DBSession()
    user_query = session.query(User).filter(User.username == username)
    if not user_query.first():
        # if the user query returns no users with the github username
        # create a new one
        user = User(username = username)
        session.add(user)
        session.commit()
    # add the unique token_hash to the DB to store github's access
    user_query.update(
            {User.token_hash: user_query.first().hash_token(access_token)})
    session.commit()
    return user_query.first()

#### main ####

def show_main(username):
    session = DBSession()
    categories = get_categories()
    latest_words = get_latest_words()
    return render_template('index.html',
            username=username,
            categories=categories,
            latest_words=latest_words
            )

#### category functions ####

def get_categories():
    session = DBSession()
    return session.query(Category).all()

def add_category(form):
    session = DBSession()
    session.add(Category(name=form['name']))
    session.commit()
    flash('category %s added!' % form['name'])

def show_category(categoryname, username):
    session = DBSession()
    words = session.query(Definition).filter(
            Definition.category_name == categoryname).all()
    return render_template('category.html',
            username=username,
            category=categoryname,
            words=words
            )

def show_delete_category(categoryname, username):
    session = DBSession()
    words = session.query(Definition).filter(
            Definition.category_name == categoryname).all()
    return render_template('category_delete.html',
            username=username,
            category=categoryname,
            words=words
            )

def delete_category(categoryname, username):
    session = DBSession()
    words = session.query(Definition).filter(
            Definition.category_name == categoryname).all()
    if not words:
        category = session.query(Category).filter(
                Category.name == categoryname)
        category.delete()
        session.commit()
        flash('category %s deleted!' % categoryname)

#### word functions ####

def get_latest_words():
    return None

def show_add_word(username):
    categories = get_categories()
    return render_template('definition_create.html',
            username = username,
            categories=categories
            )

def add_word(form, username):
    session = DBSession()
    session.add(Definition(
        word=form['word'],
        definition=form['definition'],
        category_name=form['category'],
        created_by=username
        ))
    session.commit()
    flash('word %s added!' % form['word'])
    word = session.query(Definition).filter(
            Definition.word == form['word']).one()
    return word

def show_word(word, username):
    session = DBSession()
    word = session.query(Definition).filter(
            Definition.word == word).one()
    return render_template('definition.html',
            username = username,
            word=word
            )
