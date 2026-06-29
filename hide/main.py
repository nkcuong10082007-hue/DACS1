from database.db import create_tables
from gui.home import home_screen

if __name__ == "__main__":
    create_tables()
    home_screen()
