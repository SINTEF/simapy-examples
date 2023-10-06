
# pylint: disable=unsubscriptable-object
from datetime import datetime
from pathlib import Path
import time
import numpy as np
import pandas as pd
from dmt.dmt_writer import DMTWriter

from bluesmet.normet.nora3 import arome3km_3hr

import simapy.metocean.hindcast as hc

def __create_wind(wind_name, uu, dd , height):
    # Met: North West Up, wind_going_to
    # SIMA: North East Down, wind coming from
    # SIMA direction = MET dir + 90 deg
    dir_offset = 90.0
    dir_sima = dd + dir_offset
    wind = hc.StochasticWind()
    wind.name = wind_name
    wind.level = height
    wind.speed = uu
    wind.direction = dir_sima
    return wind

def __create_hindcast(hc_name, hc_values):
    heights = hc_values["height"]
    speed = hc_values["wind_speed"]
    direction = hc_values["wind_direction"]

    winds = []

    for didx, height in enumerate(heights):
        uu = speed[:,didx]
        dd = direction[:,didx]
        wname = "Level_" + str(didx)
        winds.append(__create_wind(wname, uu, dd, height))

    # Convert Unix epoch to datetime string
    sdates = np.datetime_as_string(hc_values["time"].astype("datetime64[s]"), unit="h", timezone="UTC").astype('|S')

    hindcast = hc.Hindcast()
    hindcast.description = "Collected from norway met's: https://thredds.met.no/thredds/dodsC/nora3wavesubset_files/atm"
    hindcast.name = hc_name
    hindcast.date = sdates
    hindcast.latitude = hc_values.longitude
    hindcast.longitude = hc_values.latitude
    hindcast.wind = winds
    return hindcast


if __name__ == "__main__":
    # Start timing
    start = time.time()
    start_date = datetime(2020, 10, 21)
    end_date = datetime(2020, 11, 21)

    lon_pos = 5.835813
    lat_pos = 64.731729

    requested_values = [
        "height",
        "wind_speed",
        "wind_direction"
    ]

    values = arome3km_3hr.get_values_between(
        lat_pos, lon_pos, start_date, end_date, requested_values
    )

    # End timing and print elapsed time
    end = time.time()
    print("Elapsed time: " + str(end - start) + " seconds")

    name = "hindcast_wind_nora3"
    hindcast_data = __create_hindcast(name,values)

    dates = values["time"].values
    dstart = pd.to_datetime(dates[0])
    dend = pd.to_datetime(dates[-1])
    sd = dstart.strftime("%Y.%m.%d.%H")
    ed = dend.strftime("%Y.%m.%d.%H")
    path = Path(f"./output/simamet/{name}_{sd}-{ed}.h5")
    path.parent.mkdir(parents=True, exist_ok=True)
    DMTWriter().write(hindcast_data, path)
    print(f"Written to {path.resolve()}")
