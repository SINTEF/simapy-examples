# Examples

To run an example:

1. Navigate to the specific example directory in the `src` folder
2. Run the Python script for that example

* `src/` - Contains all example scripts
* `input/` - Contains input files used by the examples
* `output/` - Directory where script outputs are saved

The examples are organized by category, with each category focusing on different aspects of the SIMAPY package:

## SIMO

```{toctree}
:maxdepth: 1

simo/write_simo_task
simo/run_simo_condition
simo/import_hydrodynamic_coefficients
simo/create_connected_bodies
```

## RIFLEX

```{toctree}
:maxdepth: 1

riflex/read_and_write_riflex
riflex/run_parallel
```


## Workflow

```{toctree}
:maxdepth: 1

workflow/run_workflow_with_sre
workflow/run_from_stask_with_file
workflow/run_parallel
```

## Metocean

Demonstrates use of metocean data to create input to Metocean Task in SIMA

We use python libraries developed in [SFIBlues](https://sfiblues.no/) to collect metocean data from metocean data providers such as the [Norwegian Meteorological Institute](https://www.met.no/en)

See [metocean-api](https://metocean-api.readthedocs.io) and [metocean-stats](https://metocean-stats.readthedocs.io)

The generated h5/json files can be imported into the SIMA Metocan Task and then be used in further analyses

Right click Metocean Task in SIMA and choose "import metocean data", then select the generated file to import

# The following requirements are needed to run the examples

pip install -r requirements-metocean.txt

```{toctree}
:maxdepth: 1

metocean/create_excel_scatter
metocean/create_hindcast_current
metocean/create_hindcast_wave
metocean/create_hindcast_wave_wind
metocean/create_hindcast_wind
metocean/create_sima_scatter
```