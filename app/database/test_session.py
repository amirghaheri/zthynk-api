from sqlalchemy import text

from app.database.connection import SessionLocal


db = SessionLocal()

try:
    result = db.execute(text("SELECT current_database()"))
    print(result.scalar())
finally:
    db.close()