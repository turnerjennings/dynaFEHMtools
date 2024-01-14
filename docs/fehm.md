# DynaFEHMtools

The root package contains basic functions for subsetting the binary output arrays and eliminating unnecessary data from later intensive calculations (e.g., principal stresses/strains).

## __THUMS_brain_set__
Define a list with the part numbers for the [THUMS v7](https://www.toyota.co.jp/thums/?_ga=2.81170391.176877620.1617706562-672350067.1617706562) brain model.

``` python
def THUMS_brain_set(offset=0):

brain=THUMS_brain_set()
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| offset | int | Integer to default part numbers if offsetting was applied during keyword input definition |

__returns__

List of part numbers constituting THUMS white/gray matter

## __THUMS_skull_sets__
Define a list with the part numbers for the [THUMS v7](https://www.toyota.co.jp/thums/?_ga=2.81170391.176877620.1617706562-672350067.1617706562) brain model.

``` python
def THUMS_skull_sets(offset=0):

skull_solid, skull_shell=THUMS_skull_sets()
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| offset | int | Integer to default part numbers if offsetting was applied during keyword input definition |

__returns__

- List of part numbers for solid parts in THUMS skull
- List of part numbers for shell parts in THUMS skull

## __element_part_ids__
Returns a numpy array with dimensions [n_elements,1] with the part number associated with each element.  This routine can be run for solid or shell elements.

``` python
def element_part_ids(plotobject,format="solid"):

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")
shell_part_ids=element_part_ids(d3plot,"shell")
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| plotobject | lasso.dyna.D3plot | D3plot or D3part file being evaluated |
| format | String | Type of element to evaluate, either "solid" or "shell" |


__returns__

Numpy array containing part number of each element.

## __elements_in_part_set__
Subsets a list of elements to only contain elements defined by a part set.  Requires prior definition of element part ids (see element_part_id function above).

``` python
def elements_in_part_set(element_part_ids, part_list):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")
shell_part_ids=element_part_ids(d3plot,"shell")

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| element_part_ids | numpy.ndarray | List of part numbers for each solid/shell element in the database |
| part_list | list[int] | List of parts to subset |


__returns__

Array containing the indices of each element in the part subset.

## __nodes_in_element_list__
Finds the unique nodes associated with a list of elements

``` python
def nodes_in_element_list(element_list, element_indices):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

node_indices=d3plot.arrays["Element_solid_node_indexes"]

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

brain_nodes=nodes_in_element_list(brain_elements,node_indices)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| element_list | numpy.ndarray | List of elements to search for nodes |
| element_indices | numpy.ndarray | Nodal connectivity table for all elements of chosen type|


__returns__

Array containing the indices of each node connected to the specified set of elements.

## __element_list_volume_history__
Calculates the volume of each element in a given list over the timesteps in the binary file.

``` python
def element_list_volume_history(element_indices, node_coordinates, type="solid",thickness=None):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

node_indices=d3plot.arrays["Element_solid_node_indexes"]

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

node_history = d3plot.arrays["node_displacement"]

brain_volume_history = element_list_volume_history(node_indices[brain_elements, :], node_history)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| element_indices | numpy.ndarray | Nodal connectivity table for all elements which volume calculation is desired |
| node_coordinates | numpy.ndarray | Time history of the position of each node |
| type | string | Element type, "solid" or "shell" |
| thickness | float | Element thickness, must be specified if type="shell" |


__returns__

Array with dimensions [n_timesteps,n_elements] containing the volume of each element in the given subset.

## __element_centroids__
Calculates the centroid location of each element at every timestep.

``` python
def element_centroids(object, element_set):

brain_parts=THUMS_brain_set()

d3plot=D3plot("path/to/")

solid_part_ids=element_part_ids(d3plot,"solid")

brain_elements=elements_in_part_set(solid_part_ids,brain_parts)

centroids=element_centroids(d3plot,brain_elements)
```
__inputs__

| Attribute | Type | Description|
|---------|-------------|-------------|
| object | lasso.dyna.D3plot | binary plot object |
| element_set | numpy.ndarray | subset of elements to evaluate centroid history on |


__returns__

Array with dimensions [n_timesteps,n_elements_in_set,3] containing the x,y,z position of the element centroid for each timestep.



