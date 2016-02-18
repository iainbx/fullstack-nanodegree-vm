"""
SQLAlchemy database model
"""
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    items = relationship("Item", cascade="all,delete", backref="category")    
    
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return '<Category %r>' % self.name

    @property
    def serialize(self):
        return {
            'id':           self.id,
            'name':        self.name
            }

class Item(Base):
    __tablename__ = 'item'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(1000))
    pub_date = Column(DateTime)
    image = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    #category = relationship(Category)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    
    def __repr__(self):
        return '<Item %r>' % self.name

    @property
    def serialize(self):
       
       return {
           'name'         : self.name,
           'description'         : self.description,
           'id'         : self.id,
           'category_id'         : self.category_id,
           'category'         : self.category,
           'image'         : self.image
       }

