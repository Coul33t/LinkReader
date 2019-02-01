# LinkReader
A small website to read and display links from CSV files.

Requirements (all the libraries can be downloaded through `pip`):
* Python 3.7 
* Flask
* Sqlite3
* Passlib

You will also need to create a `constants.py` file in the root directory, containing:
* `SECRET_KEY`: Your API secret key
* `DATABASE`: The database location (for example `database/my_super_database.db`)
* `VIDEO_LIST`: A list of website from where video content can be pulled (e.g. `["youtube", "gfycat"]`) named 
