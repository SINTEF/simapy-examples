
# pylint: disable=unsubscriptable-object
from datetime import datetime
from pathlib import Path
import time
import numpy as np
import pandas as pd
from dmt.dmt_writer import DMTWriter

from bluesmet.normet.norkyst import zdepths_his
import simapy.metocean.hindcast as hc

def __create_current(current_name, v_north ,u_east, depth):
    # Met: North East Down, current going to
    # SIMA: North East Down, current going to
    # SIMA direction = MET dir
    vx = v_north
    vy = u_east
    speed = np.hypot(vx,vy)
    direction = np.rad2deg(np.arctan2(vy,vx))
    dir_sima = direction
    current = hc.StochasticCurrent()
    current.name = current_name
    current.level = depth
    current.speed = speed
    current.direction = dir_sima
    return current

def __create_hindcast(hc_name, hc_values):
    depths = hc_values["depth"]
    v_north = hc_values["v_northward"]
    u_east = hc_values["u_eastward"]

    currents = []

    for didx, depth in enumerate(depths):
        uu = u_east[:,didx]
        if np.ma.is_masked(uu):
            # Then there are no values for this depth
            continue
        vv = v_north[:,didx]
        current_name = "Level_" + str(didx)
        currents.append(__create_current(current_name, vv, uu, depth))

    # convert dates to strings
    # Time is given in Unix epoch
    sdates = np.datetime_as_string(hc_values["time"].astype("datetime64[s]"), unit="h", timezone="UTC").astype('|S')

    hindcast = hc.Hindcast()
    hindcast.description = "Collected from norway met's: https://thredds.met.no/thredds/dodsC/fou-hi/norkyst800m-1h/"
    hindcast.name = hc_name
    hindcast.date = sdates
    hindcast.latitude = hc_values.longitude
    hindcast.longitude = hc_values.latitude
    hindcast.current = currents
    return hindcast


if __name__ == "__main__":
    # Start timing
    start = time.time()
    start_date = datetime(2020, 10, 21)
    end_date = datetime(2020, 10, 22)

    lon_pos = 5.835813
    lat_pos = 64.731729

    requested_values = ["depth", "v_northward", "u_eastward"]

    values=zdepths_his.get_values_between(lat_pos,lon_pos,start_date, end_date, requested_values)

    # End timing and print elapsed time
    end = time.time()
    print("Elapsed time: " + str(end - start) + " seconds")

    name = "hindcast_current_n800"
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
