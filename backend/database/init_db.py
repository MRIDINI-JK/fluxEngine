from backend.database.base import Base
from backend.database.session import engine

# Import every model here
import backend.database.models


def init_database():

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")