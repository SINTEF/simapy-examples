
from pathlib import Path
import time
import numpy as np
import xarray as xr
import pandas as pd
from metocean_api import ts
from dmt.dmt_writer import DMTWriter

import simapy.metocean.hindcast as hc

def __create_current(current_name, speed ,direction, depth):
    # SIMA: North East Down, current going to
    # MET: North East Down, current coming from
    dir_sima = (180.0 + direction) % 360.0
    current = hc.StochasticCurrent()
    current.name = current_name
    current.level = depth
    current.speed = speed
    current.direction = dir_sima
    return current

def __create_hindcast(df_ts, hc_values: xr.DataArray, actual_lat, actual_lon):
    # Print all attributes
    product = df_ts.product
    name = "hindcast_current_" + product
    depths = hc_values["depth"]
    speed = hc_values["current_speed"]
    direction = hc_values["current_direction"]

    currents = []

    for didx, depth in enumerate(depths):
        speed_d = speed[:,didx]
        dir_d = direction[:,didx]
        current_name = "Level_" + str(didx)
        currents.append(__create_current(current_name, dir_d, speed_d, depth))

    # convert dates to strings
    # Time is given in Unix epoch
    sdates = np.datetime_as_string(hc_values["time"].astype("datetime64[s]"), unit="h", timezone="UTC").astype('|S')

    hindcast = hc.Hindcast()
    hindcast.description = f"Collected from norway met product {product}"
    hindcast.name = name
    hindcast.date = sdates
    hindcast.latitude = actual_lat
    hindcast.longitude = actual_lon
    hindcast.current = currents
    return hindcast


if __name__ == "__main__":
    # Start timing
    start = time.time()
    start_date ="2017-01-19"
    end_date = "2017-01-20"

    lon_pos = 5.835813
    lat_pos = 64.731729

    nc_file = f"./output/simamet/hindcast-current-{start_date}-{end_date}.nc"

    df_ts = ts.TimeSeries(
        lon=lon_pos,
        lat=lat_pos,
        datafile=nc_file,
        start_time=start_date,
        end_time=end_date,
        product="NorkystDA_zdepth",
    )
    df_ts.import_data(save_csv=False, save_nc=True, use_cache=True)

    lat_pos = df_ts.lat_data
    lon_pos = df_ts.lon_data

    # End timing and print elapsed time
    end = time.time()
    print("Elapsed time: " + str(end - start) + " seconds")

    with xr.open_dataset(df_ts.datafile) as values:
        hindcast_data = __create_hindcast(df_ts,values, lat_pos, lon_pos)
        dates = values["time"].values
        dstart = pd.to_datetime(dates[0])
        dend = pd.to_datetime(dates[-1])
        sd = dstart.strftime("%Y.%m.%d.%H")
        ed = dend.strftime("%Y.%m.%d.%H")
        path = Path(f"./output/simamet/{df_ts.product}_{sd}-{ed}.h5")
        path.parent.mkdir(parents=True, exist_ok=True)
        DMTWriter().write(hindcast_data, path)
        print(f"Written to {path.resolve()}")
