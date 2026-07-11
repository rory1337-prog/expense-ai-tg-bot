from db import models
from db.session import Base, engine


def init_app():
    Base.metadata.create_all(bind=engine)
