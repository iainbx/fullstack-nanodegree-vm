from catalog.config import *
from catalog.models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make db connection
engine = create_engine(DATABASE_URI)

# Get a db session
DBSession = sessionmaker(bind=engine)
db_session = DBSession()
    
def main():
    clearDb()

def clearDb():
    """Drop and create tables"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
def createSampleData():
    clearDb()
    u = createUser('iain','iain@gmail.com')
    c = createCategory('appetizers', u.id)

    
def createCategory(name, user_id):
    c = Category(name, user_id)
    db_session.add(c)
    db_session.commit()
    return c


def createUser(name, email):
    u = User(name=name,email=email)
    db_session.add(u)
    db_session.commit()
    return u


if __name__ == '__main__':
    main()