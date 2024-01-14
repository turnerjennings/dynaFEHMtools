# DynaFEHMtools

Extract head injury metrics from LS-DYNA binary output files.  This package contains functions for subsetting the binary array structures (dynafehmtools), as well as functions for calculating injury metrics (dynafehmtools.injurymetrics).  The objective of this package is to provide convenient data reduction for head injury analysis to reduce storage and file transfer requirements (e.g., in an HPC environment)

## Installation

Download repo and install locally using pip/docker/etc.

## Project layout

    dynafehmtools
    | - D3plot subsetting functions
    | - dynafehmtools.injurymetrics
    |   |- Head injury metric calculations

## Example

Below is an example script using the dynaFEHMtools framework to calculate the intracranial pressure for each element in the brain model of the [THUMS v7](https://www.toyota.co.jp/thums/?_ga=2.81170391.176877620.1617706562-672350067.1617706562) Finite Element Head Model.  The script also calculates the quantiles of pressure and writes both to output files. 

``` python
import dynaFEHMtools as FM
import dynaFEHMtools.injurymetrics as IM
from lasso.dyna import D3plot
import numpy as np

#define part set for brain parts
brain=FM.THUMS_brain_set()


#load d3plot
array_filter=["element_solid_stress","element_solid_strain","part_internal_energy","node_displacement"]
d3plot = D3plot(input_path, buffered_reading=True,state_array_filter=array_filter)

# define arrays of element and node ids
element_solid_indices = d3plot.arrays["element_solid_node_indexes"]

# create array of part IDs for each element
element_solid_part_ids = FM.element_part_ids(d3plot,format="solid")

# find elements that belong to the brain part set
brain_elements = FM.elements_in_part_set(element_solid_part_ids, brain)

# calculate intracranial pressure
pressure = IM.element_pressure(d3plot, brain_elements)

#calculate pressure quantiles
p99 = np.quantile(pressure, 0.99, axis=1)
p95 = np.quantile(pressure, 0.95, axis=1)
p05 = np.quantile(pressure, 0.05, axis=1)
p01 = np.quantile(pressure, 0.01, axis=1)
pout = np.stack((p99, p95, p05, p01), axis=1)

# save outputs
np.savetxt(savepath + name + "_pressure.csv", pressure, delimiter=",", fmt="%e")
np.savetxt(savepath + name + "_pressurestats.csv", pout, delimiter=",", fmt="%e")
```

