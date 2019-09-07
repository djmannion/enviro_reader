#!/usr/bin/env python

import pathlib
import time
import collections
import datetime
import time

# weather
import smbus2
import bme280
# light
import ltr559
# gas
import enviroplus.gas
# PM
import pms5003


BASE_PATH = pathlib.Path(__file__).absolute().parent.parent.parent
READINGS_PATH = BASE_PATH / "readings"

READING = collections.namedtuple(
    "reading",
    (
        "date",
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
    )
)

# time between measurements
DELTA_S = 30.0

READING_NUMBER = 0


def take_readings():

    bus = smbus2.SMBus(1)
    curr_bme280 = bme280.BME280(i2c_dev=bus)
    curr_pms5003 = pms5003.PMS5003()

    # first reading is always junk
    reading = take_reading(bme280=curr_bme280, pms5003=curr_pms5003)

    curr_date = reading.date

    keep_going = True

    while keep_going:

        day_finished = False

        filename = (
            "djm_enviro_"
            + f"{curr_date.year:d}_{curr_date.month:02d}_{curr_date.day:02d}"
            + ".tsv"
        )

        path = READINGS_PATH / filename

        write_header = not path.exists()

        with open(path, "a") as readings_file:

            if write_header:
                readings_file.write("\t".join(READING._fields) + "\n")

            while not day_finished:

                reading = take_reading(bme280=curr_bme280, pms5003=curr_pms5003)

                print(reading)

                # it is finished if the day has changed
                day_finished = reading.date.day != curr_date.day

                line = reading_to_str(reading=reading)

                readings_file.write(line + "\n")

                readings_file.flush()

                time.sleep(DELTA_S)

        # update the current date
        curr_date = reading.date


def take_reading(bme280, pms5003):

    global READING_NUMBER

    bme280.update_sensor()
    gas = enviroplus.gas.read_all()

    pm_ok = False
    pm_tries = 0

    while not pm_ok and pm_tries < 10:
        try:
            pm = pms5003.read()
            pm_ok = True
        except:
            pm_tries += 1

    if not pm_ok:
        pm1_0 = pm2_5 = pm10_0 = float("nan")
    else:
        (pm1_0, pm2_5, pm10_0) = [pm.pm_ug_per_m3(n) for n in [1.0, 2.5, 10.0]]

    reading = READING(
        date=datetime.datetime.now(),
        reading_number=READING_NUMBER,
        temperature=bme280.temperature,
        humidity=bme280.humidity,
        pressure=bme280.pressure,
        light=ltr559.get_lux(),
        proximity=ltr559.get_proximity(),
        gas_reducing=gas.reducing,
        gas_oxidising=gas.oxidising,
        gas_NH3=gas.nh3,
        PM1_0=pm1_0,
        PM2_5=pm2_5,
        PM10_0=pm10_0,
    )

    READING_NUMBER += 1

    return reading


def reading_to_str(reading):

    line = "\t".join([str(getattr(reading, field)) for field in reading._fields])

    return line


if __name__ == "__main__":
    take_readings()
