from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    uid = Column(Integer, primary_key=True)
    username = Column(String(32), index=True, unique=True)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    definitions = relationship('Definition')

    @property
    def serialize(self):
        cat_definitions = [definition.serialize_nested for
                           definition in self.definitions]
        return {
            'id': self.id,
            'name': self.name,
            'definitions': cat_definitions
        }


class Definition(Base):
    __tablename__ = 'definition'
    id = Column(Integer, primary_key=True)
    word = Column(String(80), nullable=False)
    definition = Column(String(250), nullable=False)
    created_by = Column(String(32),
                        ForeignKey('user.username'),
                        nullable=False)
    category_name = Column(String(80),
                           ForeignKey('category.name'),
                           nullable=False)

    user = relationship(User)
    category = relationship(Category)

    @property
    def serialize_nested(self):
        return {
            'id':   self.id,
            'word': self.word,
            'definition': self.definition,
            'created_by': self.created_by,
        }

    @property
    def serialize(self):
        return {
            'id':   self.id,
            'word': self.word,
            'definition': self.definition,
            'created_by': self.created_by,
            'category': self.category_name,
        }


engine = create_engine('sqlite:///dictionary.db')
Base.metadata.create_all(engine)
