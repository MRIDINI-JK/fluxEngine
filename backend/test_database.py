from backend.database.health import check_database

if check_database():
    print("Database Connected")
else:
    print("Database Failed")