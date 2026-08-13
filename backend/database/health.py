from sqlalchemy import text

from backend.database import SessionLocal


def check_database():

    try:

        db = SessionLocal()

        db.execute(text("SELECT 1"))

        db.close()

        return True

    except Exception as e:

        print(e)

        return False