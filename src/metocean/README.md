# Demonstrates use of metocean data to create input to Metocean Task in SIMA

We use the python library developed in [SFIBlues](https://sfiblues.no/) to collect metocean data from metocean data providers such as the Norwegian Meteorological Institute

See [SFIBlues metocean library](https://github.com/SINTEF/blues-metocean-lib)

The generated h5/json files can be imported into the SIMA Metocan Task and then be used in further analyses

# The following requirements are needed to run the examples

pip install bluesmet netCDF4 scipy pandas xarray