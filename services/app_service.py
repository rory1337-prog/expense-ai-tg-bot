from db.session import Base, engine
from db import models

def init_app():
    Base.metadata.create_all(bind=engine)