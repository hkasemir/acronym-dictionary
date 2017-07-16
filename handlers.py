from flask import render_template, flash, jsonify, session as login_session
from models import Base, User, Definition, Category
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from application import getUsername

engine = create_engine('sqlite:///dictionary.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# user ####################


def getAvatar():
    if 'avatar_url' in login_session:
        return login_session['avatar_url']
    return None


def get_or_create_user(username, access_token):
    session = DBSession()
    user_query = session.query(User).filter(User.username == username)
    if not user_query.one():
        # if the user query returns no users with the github username
        # create a new one
        user = User(username=username)
        session.add(user)
        session.commit()
    return user_query.one()


# main ####################


def show_main():
    session = DBSession()
    categories = get_categories()
    latest_words = get_latest_words()
    return render_template('index.html',
                           username=getUsername(),
                           categories=categories,
                           latest_words=latest_words,
                           avatar_url=getAvatar()
                           )


def get_words_json():
    session = DBSession()
    words = session.query(Definition).all()
    return jsonify(Definition=[w.serialize for w in words])


def get_single_word_json(word):
    session = DBSession()
    definition = session.query(Definition).filter(
            Definition.word == word).one()
    return jsonify(Definition=[definition.serialize])


def get_categories_json():
    session = DBSession()
    categories = session.query(Category).all()
    return jsonify(Category=[c.serialize for c in categories])


# category functions ####################


def get_categories():
    session = DBSession()
    return session.query(Category).all()


def add_category(form):
    session = DBSession()
    session.add(Category(name=form['name']))
    session.commit()
    flash('category %s added!' % form['name'], 'success')


def category_has_words(categoryname):
    # since categories can only be deleted if they have no words,
    # this utility function returns a boolean for a quick check
    session = DBSession()
    a_word = session.query(Definition).filter(
            Definition.category_name == categoryname).first()
    return a_word is not None


def show_add_category():
    session = DBSession()
    categories = get_categories()
    return render_template('category_create.html',
                           username=getUsername(),
                           categories=categories,
                           avatar_url=getAvatar()
                           )


def show_category(categoryname):
    session = DBSession()
    categories = get_categories()
    words = session.query(Definition).filter(
            Definition.category_name == categoryname).all()
    return render_template('category.html',
                           username=getUsername(),
                           category=categoryname,
                           categories=categories,
                           words=words,
                           avatar_url=getAvatar()
                           )


def show_delete_category(categoryname):
    categories = get_categories()
    return render_template('category_delete.html',
                           username=getUsername(),
                           category=categoryname,
                           categories=categories,
                           avatar_url=getAvatar()
                           )


def delete_category(categoryname):
    if not category_has_words(categoryname):
        session = DBSession()
        category = session.query(Category).filter(
                Category.name == categoryname)
        category.delete()
        session.commit()
        flash('category %s deleted!' % categoryname, 'success')


# word functions ####################


def get_latest_words():
    session = DBSession()
    words = session.query(Definition).limit(10)
    return words


def user_created_word(word):
    # boolean whether the user is the owner of the word
    session = DBSession()
    definition = session.query(Definition).filter(
            Definition.word == word).one()
    return definition.created_by == getUsername()


def show_add_word():
    categories = get_categories()
    return render_template('definition_create.html',
                           username=getUsername(),
                           categories=categories,
                           avatar_url=getAvatar()
                           )


def add_word(form):
    session = DBSession()
    session.add(Definition(
        word=form['word'],
        definition=form['definition'],
        category_name=form['category'],
        created_by=getUsername()
        ))
    session.commit()
    flash('%s added!' % form['word'], 'success')
    word = session.query(Definition).filter(
            Definition.word == form['word']).one()
    return word


def show_word(word):
    session = DBSession()
    categories = get_categories()
    definition = session.query(Definition).filter(
            Definition.word == word).one()
    return render_template('definition.html',
                           username=getUsername(),
                           categories=categories,
                           word=definition,
                           avatar_url=getAvatar()
                           )


def show_edit_word(word):
    session = DBSession()
    categories = get_categories()
    definition = session.query(Definition).filter(
            Definition.word == word).one()
    return render_template('definition_edit.html',
                           username=getUsername(),
                           categories=categories,
                           word=definition,
                           avatar_url=getAvatar()
                           )


def edit_word(old_word, form):
    if user_created_word(old_word):
        session = DBSession()
        word = session.query(Definition).filter(
                Definition.word == old_word).one()
        word.word = form['word']
        word.definition = form['definition']
        session.add(word)
        session.commit()
        flash('%s edited!' % form['word'], 'success')
        updated = session.query(Definition).filter(
                Definition.id == word.id).one()
        return updated


def show_delete_word(word):
    session = DBSession()
    categories = get_categories()
    definition = session.query(Definition).filter(
            Definition.word == word).one()
    return render_template('definition_delete.html',
                           username=getUsername(),
                           categories=categories,
                           word=definition,
                           avatar_url=getAvatar()
                           )


def delete_word(word):
    if user_created_word(word):
        session = DBSession()
        deleted = session.query(Definition).filter(
                Definition.word == word)
        categoryname = deleted.one().category_name
        deleted.delete()
        session.commit()
        flash('%s deleted!' % word, 'success')
        return categoryname
