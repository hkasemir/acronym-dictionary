from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class User(Base):
    __tablename__ = 'user'
    uid = Column(Integer, primary_key=True)
    username = Column(String(32), index=True, unique=True)
    token_hash = Column(String(64))

    def hash_token(self, token):
        self.token_hash = pwd_context.encrypt(token)

    def verify_token(self, token):
        return pwd_context.verify(token, self.token_hash)

    def generate_auth_cookie(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'uid': self.uid })

    @staticmethod
    def verify_auth_cookie(cookie):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(cookie)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['uid']
    	return user_id


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Definition(Base):
    __tablename__ = 'definition'
    id = Column(Integer, primary_key=True)
    word = Column(String(80), nullable=False)
    definition = Column(String(250), nullable=False)
    created_by = Column(String(32), ForeignKey('user.username'), nullable=False)
    category = Column(Integer, ForeignKey('category.name'), nullable=False)

    user = relationship(User, foreign_keys=[created_by])
    category = relationship(Category, foreign_keys=[category])
    @property
    def serialize(self):
        return {
            'id':   self.id,
            'word': self.word,
            'definition': self.definition,
            'created_by': self.created_by,
            'category': self.category,
        }


engine = create_engine('sqlite:///dictionary.db')
Base.metadata.create_all(engine)
