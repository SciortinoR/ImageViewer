from app import App
from database import Database

# Setup GUI and Database
if __name__ == '__main__':
    database = Database()
    app = App(database)
    app.Run()

