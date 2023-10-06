"""Create a scatter table from wave data and save it to an Excel file"""
from datetime import datetime
from pathlib import Path

from bluesmet.common.scatter import Scatter
from bluesmet.normet.nora3 import wave_sub_time

from simapy.metocean.scatter.scatter import Scatter as SimaScatter
from simapy.metocean.scatter.sector import Sector
from simapy.metocean.scatter.wave import Wave
from dmt.dmt_writer import DMTWriter


def _create_scatter(scatter: Scatter) -> SimaScatter:
    sima_scatter = SimaScatter()
    sima_scatter.name = "Scatter"
    sima_scatter.description = "Scatter table created from Nora3 wave data"
    hs = scatter.row_values()
    tp = scatter.column_values()
    occurences = scatter.occurences()

    sima_scatter.hsUpperLimits = hs
    sima_scatter.tpUpperLimits = tp

    omni = Sector()
    omni.name = "Omni"
    omni.description = "Omni-directional"
    sima_scatter.omni = omni
    wave = Wave()
    wave.occurrence = occurences
    omni.wave = wave
    return sima_scatter


def write_scatter():
    """Write a scatter table to an excel file"""
    lat_pos = 62.5365
    lon_pos = 4.1770
    start_date = datetime(2020, 10, 21)
    end_date = datetime(2020, 11, 21)
    requested_values = ["hs", "tp"]
    values = wave_sub_time.get_values_between(
        lat_pos, lon_pos, start_date, end_date, requested_values
    )

    bin_size = 2.0
    scatter = Scatter(bin_size=bin_size)
    for hs, tp in zip(values["hs"], values["tp"]):
        scatter.add(hs, tp)

    sima_scatter = _create_scatter(scatter)

    sd = start_date.strftime("%Y.%m.%d.%H")
    ed = end_date.strftime("%Y.%m.%d.%H")
    path = Path(f"./output/simamet/scatter_{sd}-{ed}.h5")
    path.parent.mkdir(parents=True, exist_ok=True)
    DMTWriter().write(sima_scatter, path)
    print(f"Saved to {path.resolve()}")


if __name__ == "__main__":
    write_scatter()
