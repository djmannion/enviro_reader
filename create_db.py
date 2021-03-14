import sqlite3
import pathlib
import datetime

import mariadb


def run():

    readings_path = pathlib.Path("~/readings").expanduser()

    db_path = readings_path / "djm_enviro_readings.db"

    sqlite_db = sqlite3.connect(database=db_path)
    sqlite_cursor = sqlite_db.cursor()

    mariadb_settings_path = pathlib.Path("~/.readings_server.cnf").expanduser()

    mariadb_db = mariadb.connect(default_file=SETTINGS_PATH)
    mariadb_cursor = mariadb_db.cursor()



    db.close()


if __name__ == "__main__":
    run()
