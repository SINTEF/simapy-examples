"""Create a scatter table from wave and wind data downloaded by the (sfiblues metocean library)[https://github.com/SINTEF/blues-metocean-lib]
and save it as sima metocean scatter data"""
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
import bluesmet.common.scatter as bluesmet
import simapy.metocean.scatter as simamet
from bluesmet.normet.nora3 import wave_sub_time
from dmt.dmt_writer import DMTWriter
from stats import calculate_scatter


def _create_sima_scatter(
    scatter: bluesmet.Scatter, description: str
) -> simamet.Scatter:
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

    wdir = scatter.get_values("wind_dir")
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
    requested_values = ["hs", "tp", "thq", "ff", "dd"]
    md = wave_sub_time.get_metadata()
    url = md["global"]["url"]
    values = wave_sub_time.get_values_between(
        lat_pos, lon_pos, start_date, end_date, requested_values
    )

    output = Path("./output/simamet")
    output.mkdir(parents=True, exist_ok=True)

    directions = values["thq"]
    # TODO: Change to SIMA metocean system

    # Divide directions into sectors from 0 to 360

    # Define the bin size
    sector_size = 30.0

    # Define the bin edges
    bin_edges = np.arange(0, 360 + sector_size, sector_size)

    # Get the bin indices for each direction
    bin_indices = np.digitize(directions, bin_edges)

    all_hs = values["hs"]
    all_tp = values["tp"]

    scatter_bin_size = 1.0

    sima_scatter = simamet.Scatter()
    sima_scatter.name = "Scatter"

    sctr=calculate_scatter(all_hs, all_tp,1.0)
    sctr=calculate_scatter(all_hs, all_tp,2.0)
    sctr=calculate_scatter(all_hs, all_tp,4.0)
    sctr=calculate_scatter(all_hs, all_tp,0.8)
    sctr=calculate_scatter(all_hs, all_tp,0.5)
    # print(sctr)
    scatter = bluesmet.Scatter(bin_size=scatter_bin_size)
    for hs, tp in zip(all_hs, all_tp):
        scatter.add(hs, tp)

    hs_upper = scatter.row_values()
    tp_upper = scatter.column_values()
    all = scatter.occurences()
    # TODO: Create OMNI!

    sima_scatter.hsUpperLimits = hs_upper
    sima_scatter.tpUpperLimits = tp_upper

    sectors = list()


    # Loop over the range from 1 to the number of bins + 1
    for bin_number in range(1, len(bin_edges)):
        # Find the indices in bin_indices that match the bin number
        indices = [i for i, x in enumerate(bin_indices) if x == bin_number]
        dirs_for_sector = directions[indices]
        hs_for_sector = all_hs[indices]
        tp_for_sector = all_tp[indices]
        
        sector_scatter = bluesmet.Scatter(bin_size=scatter_bin_size)
        for hs, tp in zip(hs_for_sector, tp_for_sector):
            sector_scatter.add(hs, tp)
        
        
        sctr2=calculate_scatter(hs_for_sector,tp_for_sector,scatter_bin_size)
        
        # print(calculate_scatter(hs_for_sector,tp_for_sector,scatter_bin_size*2))
        # print(calculate_scatter(hs_for_sector,tp_for_sector,scatter_bin_size/2))

        sector_dir = bin_edges[bin_number-1]
        sector = simamet.Sector()
        sector.name = f"Sector: {sector_dir} deg"
        sector.direction = sector_dir
        dir_min = dirs_for_sector.min()
        dir_mean = dirs_for_sector.mean()
        dir_max = dirs_for_sector.max()
        dir_std = dirs_for_sector.std()
        sector.description = (
            f"Sector data: min={dir_min} mean={dir_mean} max={dir_max} std={dir_std}"
        )

        sector_occurence = sector_scatter.occurences()
        assert sector_occurence.shape == all.shape

        wave = simamet.Wave()
        wave.occurrence = sector_occurence
        sector.wave = wave

        sectors.append(sector)

    sima_scatter.sectors = sectors

    sd = start_date.strftime("%Y.%m.%d.%H")
    ed = end_date.strftime("%Y.%m.%d.%H")

    prefix = f"directional_scatter_{sd}-{ed}"

    description = f"Created with data from met.no\nFrom {sd} to {ed} at latitude={lat_pos}, longitude={lon_pos}\nSee {url}"
    sima_scatter.description = description

    path = output / f"{prefix}.h5"
    DMTWriter().write(sima_scatter, path)
    print(f"Saved to {path.resolve()}")


if __name__ == "__main__":
    create_scatter()
