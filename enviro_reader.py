#!/usr/bin/env python

import pathlib
import time
import collections
import datetime
import contextlib
import sqlite3

# weather
import smbus2
import bme280

# light
import ltr559

# gas
import enviroplus.gas

# PM
import pms5003


READINGS_PATH = pathlib.Path("~/readings").expanduser()
DB_PATH = READINGS_PATH / "djm_enviro_readings.db"

assert DB_PATH.exists()

READING = collections.namedtuple(
    "reading",
    (
        "timestamp",
        "reading_number",
        "temperature",
        "humidity",
        "pressure",
        "light",
        "proximity",
        "gas_reducing",
        "gas_oxidising",
        "gas_NH3",
        "PM1_0",
        "PM2_5",
        "PM10_0",
    ),
)

# time between measurements
DELTA_S = 30.0

BUS = smbus2.SMBus(1)
BME280 = bme280.BME280(i2c_dev=BUS)
PMS5003 = pms5003.PMS5003()


def take_readings():

    reading_number = 0

    # first reading is always junk
    reading = take_reading(reading_number=reading_number)

    reading_number += 1

    insert_str = (
        "INSERT INTO readings VALUES ("
        + ",".join(["?"] * len(reading))
        + ")"
    )

    with contextlib.closing(sqlite3.connect(database=DB_PATH)) as db:

        cursor = db.cursor()

        keep_going = True

        while keep_going:

            reading = take_reading(reading_number=reading_number)

            with db:
                cursor.execute(insert_str, reading)

            reading_number += 1

            print(reading)

            time.sleep(DELTA_S)



def take_reading(reading_number):

    BME280.update_sensor()
    gas = enviroplus.gas.read_all()

    pm_ok = False
    pm_tries = 0

    while not pm_ok and pm_tries < 10:
        try:
            pm = PMS5003.read()
            pm_ok = True
        except:
            pm_tries += 1

    if not pm_ok:
        pm1_0 = pm2_5 = pm10_0 = float("nan")
    else:
        (pm1_0, pm2_5, pm10_0) = [pm.pm_ug_per_m3(n) for n in [1.0, 2.5, 10.0]]

    reading = READING(
        date=datetime.datetime.now().isoformat(),
        reading_number=reading_number,
        temperature=BME280.temperature,
        humidity=BME280.humidity,
        pressure=BME280.pressure,
        light=ltr559.get_lux(),
        proximity=ltr559.get_proximity(),
        gas_reducing=gas.reducing,
        gas_oxidising=gas.oxidising,
        gas_NH3=gas.nh3,
        PM1_0=pm1_0,
        PM2_5=pm2_5,
        PM10_0=pm10_0,
    )

    return reading


if __name__ == "__main__":
    take_readings()
