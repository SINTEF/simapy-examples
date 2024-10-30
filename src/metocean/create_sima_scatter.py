
"""
Create a scatter table using (metocean stats library)[https://metocean-stats.readthedocs.io]
and save it as SIMA metocean scatter data

Right click Metocean Task in SIMA and choose "import metocean data", then select the generated file to import

"""
from pathlib import Path
import pandas as pd
from metocean_api import ts
from metocean_stats.stats.general import calculate_scatter
from simapy.metocean.scatter.scatter import Scatter as SimaScatter
from simapy.metocean.scatter.sector import Sector
from simapy.metocean.scatter.wave import Wave
from dmt.dmt_writer import DMTWriter


def _create_sima_scatter(scatter: pd.DataFrame) -> SimaScatter:
    sima_scatter = SimaScatter()
    sima_scatter.name = "Scatter"
    hs = scatter.index
    tp = scatter.columns
    occurences = scatter.values

    sima_scatter.hsUpperLimits = hs
    sima_scatter.tpUpperLimits = tp

    omni = Sector()
    omni.name = "Omni"
    omni.description = f"Omni-directional scatter table created from product {product} for the period {start_date} to {end_date}"
    sima_scatter.omni = omni
    wave = Wave()
    wave.occurrence = occurences
    omni.wave = wave
    return sima_scatter

lat_pos = 62.5365
lon_pos = 4.1770
start_date = "2020-10-21"
end_date = "2020-11-21"

product = "NORA3_wave_sub"
var1_name = "hs"
var2_name = "tp"

var1_block_size = 1.0
var2_block_size = 2.0

requested_values = [var1_name, var2_name]

df_ts = ts.TimeSeries(
    lon=lon_pos,
    lat=lat_pos,
    start_time=start_date,
    end_time=end_date,
    variable=requested_values,
    product=product,
)

df_ts.import_data(save_csv=False, save_nc=False, use_cache=True)

scatter: pd.DataFrame = calculate_scatter(df_ts.data, var1_name, var1_block_size, var2_name, var2_block_size)

sima_scatter = _create_sima_scatter(scatter)

path = Path(f"./output/simamet/scatter_{product}-{start_date}-{end_date}.h5")
path.parent.mkdir(parents=True, exist_ok=True)
DMTWriter().write(sima_scatter, path)
print(f"Saved to {path.resolve()}")
