import sqlite3
import pathlib
import datetime


def run():

    readings_path = pathlib.Path("~/readings").expanduser()

    txt_paths = readings_path.glob("djm_enviro_*.tsv")

    db_path = readings_path / "djm_enviro_readings.db"

    db = sqlite3.connect(database=db_path)

    with db:

        cursor = db.cursor()

        cursor.execute("DROP TABLE IF EXISTS readings")

        cursor.execute(
            (
                "CREATE TABLE readings("
                + "timestamp DATETIME,"
                + "reading_number NUMERIC,"
                + "temperature NUMERIC,"
                + "humidity NUMERIC,"
                + "pressure NUMERIC,"
                + "light NUMERIC,"
                + "proximity NUMERIC,"
                + "gas_reducing NUMERIC,"
                + "gas_oxidising NUMERIC,"
                + "gas_nh4 NUMERIC,"
                + "PM1_0 NUMERIC,"
                + "PM2_5 NUMERIC,"
                + "PM10_0 NUMERIC"
                + ")"
            )
        )

        for txt_path in txt_paths:

            raw = txt_path.read_text().splitlines()

            for row in raw[1:]:

                data = row.split("\t")

                if not data:
                    continue

                try:
                    timestamp = datetime.datetime.fromisoformat(data[0]).isoformat()
                except ValueError:
                    continue
                timestamp = "'" + timestamp + "'"

                insert_str = (
                    "INSERT INTO readings VALUES(" + ", ".join([timestamp] + data[1:]) + ")"
                )

                insert_str = insert_str.replace("nan", "NULL")

                try:
                    cursor.execute(insert_str)
                except ValueError:
                    print(insert_str)

    db.close()


if __name__ == "__main__":
    run()
