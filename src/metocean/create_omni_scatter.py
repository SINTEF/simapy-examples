"""Create a scatter table from wave and wind data downloaded by the (sfiblues metocean library)[https://github.com/SINTEF/blues-metocean-lib]
and save it as sima metocean scatter data"""
from datetime import datetime
from pathlib import Path

import bluesmet.common.scatter as bluesmet
import simapy.metocean.scatter as simamet
from bluesmet.normet.nora3 import wave_sub_time
from dmt.dmt_writer import DMTWriter

def _create_sima_scatter(scatter: bluesmet.Scatter, description: str) -> simamet.Scatter:
    sima_scatter = simamet.Scatter()
    sima_scatter.name = "Scatter"
    hs = scatter.row_values()
    tp = scatter.column_values()
    occurences = scatter.occurences()

    sima_scatter.hsUpperLimits = hs
    sima_scatter.tpUpperLimits = tp

    omni = simamet.Sector()
    omni.name = "Omni"
    omni.description = description
    sima_scatter.omni = omni
    wave = simamet.Wave()
    wave.occurrence = occurences
    omni.wave = wave

    wdir=scatter.get_values("wind_dir")
    wspeed = scatter.get_values("wind_speed")
    wc = simamet.WindCurrent()
    # Assumption on level, as the dataset does not state the reference height
    wc.level = 10.0
    wc.speed = wspeed
    # We need to convert the wind direction to match the system for Metocean task in SIMA
    # Met: North West Up, wind_going_to
    # SIMA: North East Down, wind coming from
    # SIMA direction = MET dir + 90 deg
    # Add 90 to the directions where occurences is larger than 0
    wdir[occurences > 0] += 90
    wc.direction = wdir
    omni.wind = [wc]
    return sima_scatter


def create_scatter():
    """Write a scatter table to an excel file and sima metocean data"""
    lat_pos = 62.5365
    lon_pos = 4.1770
    start_date = datetime(2020, 10, 21)
    end_date = datetime(2020, 11, 21)
    requested_values = ["hs", "tp","thq","ff","dd"]
    md = wave_sub_time.get_metadata()
    url = md["global"]["url"]
    values = wave_sub_time.get_values_between(
        lat_pos, lon_pos, start_date, end_date, requested_values
    )

    output = Path("./output/simamet")
    output.mkdir(parents=True, exist_ok=True)

    bin_size = 2.0
    scatter = bluesmet.Scatter(bin_size=bin_size)
    for hs, tp,ff,dd in zip(values["hs"], values["tp"],values["ff"],values["dd"]):
        # FIXME: Orientering
        scatter.add(hs, tp,wind_dir=dd,wind_speed=ff)

    sd = start_date.strftime("%Y.%m.%d.%H")
    ed = end_date.strftime("%Y.%m.%d.%H")

    prefix = f"omnidir_scatter_{sd}-{ed}"

    description = f"Created with data from met.no\nFrom {sd} to {ed} at latitude={lat_pos}, longitude={lon_pos}\nSee {url}"
    sima_scatter = _create_sima_scatter(scatter,description)

    path = output / f"{prefix}.h5"
    DMTWriter().write(sima_scatter, path)
    print(f"Saved to {path.resolve()}")


if __name__ == "__main__":
    create_scatter()
