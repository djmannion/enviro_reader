import sqlite3
import pathlib
import datetime

import mariadb

import enviro_reader


def run():

    readings_path = pathlib.Path("~/readings").expanduser()

    db_path = readings_path / "djm_enviro_readings.db"

    sqlite_db = sqlite3.connect(database=db_path)
    sqlite_cursor = sqlite_db.cursor()

    mariadb_settings_path = pathlib.Path("~/.readings_server.cnf").expanduser()

    mariadb_db = mariadb.connect(default_file=str(mariadb_settings_path))
    mariadb_cursor = mariadb_db.cursor()

    old = sqlite_cursor.execute("SELECT * FROM readings")

    for old_reading in old:

        reading = enviro_reader.READING(*old_reading)

        enviro_reader.store_reading(
            reading=reading, cursor=mariadb_cursor, mode="REPLACE"
        )

        mariadb_db.commit()

    mariadb_db.close()
    db.close()


if __name__ == "__main__":
    run()
