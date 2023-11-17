"""Read wave data from nora3 and generate metocean hindcast readable from SIMA"""
import time as hours
from datetime import datetime
from pathlib import Path

import pandas as pd
import simapy.metocean.longTermStatistics as lstats
from bluesmet.normet.nora3 import wave_sub_time
from bluesmet.normet.metengine import extreme_stats
from dmt.dmt_writer import DMTWriter
from simapy.metocean.longTermStatistics.wave import sector, stat


def __create_longterm_statistics(hc_name, values,durationInHours, description: str):
    lts = lstats.LongTermStats()
    lts.description = description
    lts.name = hc_name

    hs_values = values["hs"]
    tp_values = values["tp"]
    return_periods=[50,100]
    res=extreme_stats.joint_2D_contour(hs_values,tp_values,return_periods)
    period = lstats.Period()
    period.name = "year"
    wave = stat.Stat()
    wave.duration = durationInHours
    omniStat = sector.Sector()
    contour = sector.Contour()
    contour.Hs = hs_values
    omniStat.contours = [contour]
    wave.omni = omniStat
    period.wave = [wave]
    lts.periods = [period]

    return lts


if __name__ == "__main__":
    # Start timing
    start = hours.time()
    start_date = datetime(2020, 10, 21)
    end_date = datetime(2020, 11, 21)

    values = {
        "longitude": 5.835813,
        "latitude": 64.731729,
    }

    lon_pos = 5.835813
    lat_pos = 64.731729

    requested_values = [
        "hs",
        "tp",
        "thq",
        "hs_sea",
        "tp_sea",
        "thq_sea",
        "hs_swell",
        "tp_swell",
        "thq_swell",
        "ff",
        "dd"
    ]

    values = wave_sub_time.get_values_between(
        lat_pos, lon_pos, start_date, end_date, requested_values
    )

    # End timing and print elapsed time
    end = hours.time()
    print("Elapsed time: " + str(end - start) + " seconds")

    dates = values["time"].values
    dstart = pd.to_datetime(dates[0])
    dend = pd.to_datetime(dates[-1])
    # Get duration in hours between two sample dates
    dur = (dates[1] - dates[0]).total_seconds() / 3600

    sd = dstart.strftime("%Y.%m.%d.%H")
    ed = dend.strftime("%Y.%m.%d.%H")

    md = wave_sub_time.get_metadata()
    url = md["global"]["url"]
    desc = f"Created with data from met.no\nFrom {sd} to {ed} at latitude={lat_pos}, longitude={lon_pos}\nSee {url}"
    name = "lts_waves_nora3"
    lts_data = __create_longterm_statistics(name, values,dur,desc)

    path = Path(f"./output/simamet/{name}_{sd}-{ed}.h5")
    path.parent.mkdir(parents=True, exist_ok=True)
    DMTWriter().write(lts_data, path)
    print(f"Written to {path.resolve()}")
