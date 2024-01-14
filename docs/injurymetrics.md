# DynaFEHMtools.injurymetrics

The injury metrics package contains the calculations for different conventional head injury metrics.

## __element_pressure__
Calculates the hydrostatic pressure (i.e., intracranial pressure) for a given list of elements

``` python
def element_pressure(object, element_set, type="solid", state_subset=None):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

icp=element_pressure(d3plot, brain_elements)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| object | lasso.dyna.D3plot | Binary plot object to evaluate |
| element_set | numpy.ndarray | Array of element indices to evaluate pressure on |
| type | string | element type being evaluated, options are "solid", "shell", or "tshell" |
| state_subset | numpy.ndarray | array of timesteps to evaluate pressure at if a subset of the total time is desired |

__returns__

Array with dimensions [n_timesteps, n_elements] containing the pressure of each element.

## __mps_mss__
Returns the principal and maximum shear stresses or strains for a given subset of elements at the timesteps specified.

``` python
def mps_mss(object, element_set, stressstrain="stress",type="solid",state_subset=None):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

mpstress, msstress=mps_mss(d3plot, brain_elements, stressstrain="stress")
mpstrain, msstrain=mps_mss(d3plot, brain_elements, stressstrain="strain")
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| object | lasso.dyna.D3plot | Binary plot object to evaluate |
| element_set | numpy.ndarray | Array of element indices to evaluate principal stresses/strains on |
| stressstrain | string | Specify whether stress or strain will be evaluated, options are "stress" or "strain" |
| type | string | element type being evaluated, options are "solid", "shell", or "tshell" |
| state_subset | numpy.ndarray | array of timesteps to evaluate principal stresses/strains at if a subset of the total time is desired |

__returns__

- Array with dimensions [n_timesteps, n_elements, 3] containing the principal stresses/strains of each element in the subset at the given time points.  Principal values are in descending order.
- Array with dimensions [n_timesteps, n_elements, 1] containing the maximum shear stress/strain of each element in the subset at the given time points.

## __von_mises__
Returns the von mises stresses for a given subset of elements at the timesteps specified.

``` python
def von_mises(object, element_set, state_subset=None):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

vmstress=von_mises(d3plot,brain_elements)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| object | lasso.dyna.D3plot | Binary plot object to evaluate |
| element_set | numpy.ndarray | Array of element indices to evaluate von mises stress on |
| state_subset | numpy.ndarray | array of timesteps to evaluate von mises stress at if a subset of the total time is desired |

__returns__

Array with dimensions [n_timesteps, n_elements] containing the von mises stress of each element in the subset at the given time points.  

## __internal_energy__
Returns the internal energy for a given part set.

``` python
def internal_energy(object, partset, state_subset=None):

skull_solid, skull_shell=THUMS_skull_sets()

d3plot=D3plot("path/to/")

solid_energy=internal_energy(d3plot,skull_solid)
shell_energy=internal_energy(d3plot,skull_shell)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| object | lasso.dyna.D3plot | Binary plot object to evaluate |
| part_set | list[int] | Array of part numbers to evaluate internal energy on |
| state_subset | numpy.ndarray | array of timesteps to evaluate internal energy at if a subset of the total time is desired |

__returns__

Array with dimensions [n_timesteps, n_parts] containing the internal energy of each part in the subset at the given time points.  


## __internal_energy__
Calculates Cumulative Strain Damage Measures for a given set of elements.  Requires prior calculation of principal strains and volume history.

``` python
def csdm(MPS, volume):

skull_solid, skull_shell=THUMS_skull_sets()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

mpstress, msstress=mps_mss(d3plot, brain_elements, stressstrain="stress")
mpstrain, msstrain=mps_mss(d3plot, brain_elements, stressstrain="strain")

node_history = d3plot.arrays["node_displacement"]

brain_volume_history = element_list_volume_history(node_indices[brain_elements, :], node_history)

survival, csdm15, csdm25, VSM=csdm(mpstrain,brain_volume_history)

```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| MPS | numpy.ndarray | Array containing the principal strain history of a specified element set |
| volume | numpy.ndarray | Array containing teh volume history of a specified element set|


__returns__
- Float representing the volume fraction of elements which exceeded a maximum principal strain of 0.15
- Float representing the volume fraction of elements which exceeded a maximum principal strain of 0.25
- Float representing the Volume Strain Metric
- Array of dimensions [1000,1] representing the volume fraction of elements which exceeded specified strain thresholds. 