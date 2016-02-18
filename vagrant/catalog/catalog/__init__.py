import catalog.config
from flask import Flask
from .models import Base, Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# init flask
app = Flask(__name__)
app.config.from_object('catalog.config')

engine = create_engine(config.DATABASE_URI)
    
#Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()



import catalog.views


