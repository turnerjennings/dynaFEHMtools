from lasso.dyna import D3plot
import numpy as np
import scipy.spatial as sps
import csv
import time
from datetime import datetime

# *****************************USER INPUTS****************************
filepaths_to_analyse = [""]


# define brain and skull part numbers
def brain_set(offset=0):
    """
    Return integer list

    Used to call the Part IDs of the 12 parts that constitute the THUMS brain.
    Can apply a static offset to the part numbers if the offset from k file
    creation is known.
    """
    brain_part_ids = [
        88000100,
        88000101,
        88000102,
        88000103,
        88000104,
        88000105,  # right brain
        88000120,
        88000121,
        88000122,
        88000123,
        88000124,
        88000125,  # left skull
    ]

    return [i + offset for i in brain_part_ids]


def skull_sets(offset=0):
    """
    Return two integer lists (solid_ids, shell_ids)

    Used to call the Part IDs of the shell and solid elements in the THUMS skull.
    Includes skull sutures and shell parts.
    Can apply a static offset to the part numbers if the offset from the k file
    creation is known
    """
    skull_solid_part_ids = [
        88000001,
        88000004,
        88000007,
        88000011,
        88000014,
        88000017,
        88000021,
        88000026,
        88000030,
        88000033,
        88000036,
        88000039,
        88000040,
        88000041,
        88000042,
        88000043,
        88000044,
        88000045,
        88000046,
        88000049,
        88000050,
        88000051,  # right skull (+ center)
        88000052,
        88000055,
        88000058,
        88000062,
        88000065,
        88000068,
        88000071,
        88000075,
        88000079,
        88000082,
        88000085,
        88000088,
        88000089,
        88000090,
        88000091,
        88000092,
        88000093,
        88000094,
        88000095,
        88000098,
        88000099,  # left skull
    ]

    skull_shell_part_ids = [
        88000002,
        88000003,
        88000005,
        88000006,
        88000008,
        88000009,
        88000010,
        88000012,
        88000013,
        88000015,
        88000016,
        88000018,
        88000019,
        88000020,
        88000022,
        88000023,
        88000024,
        88000025,
        88000027,
        88000028,
        88000029,
        88000031,
        88000032,
        88000034,
        88000035,
        88000037,
        88000038,
        88000047,
        88000048,  # right skull
        88000053,
        88000054,
        88000056,
        88000057,
        88000059,
        88000060,
        88000061,
        88000063,
        88000064,
        88000066,
        88000067,
        88000069,
        88000070,
        88000072,
        88000073,
        88000076,
        88000077,
        88000078,
        88000080,
        88000081,
        88000083,
        88000084,
        88000086,
        88000087,
        88000096,
        88000097,  # left skull
    ]
    return [i + offset for i in skull_solid_part_ids], [
        i + offset for i in skull_shell_part_ids
    ]



# function to return arrays of the part numbers associated with each element
# return: array of part numbers (n_solids), array of part numbers (n_shells)
def element_part_ids(plotobject: D3plot,format="solid"):
    '''
    Returns array with size (n_solids) with part ID from each solid element
    Returns array with size (n_shells) with part ID from each shell element
    
    Converts the part indexes arrays which give the index [0:n_parts] of the
    associated parts to to arrays which give the assigned part ID from the input
    k deck.
    '''
    part_ids = plotobject.arrays["part_ids"]
    
    if format=="solid":
        solid_ids = plotobject.arrays["element_solid_part_indexes"]
        part_numbers = part_ids[solid_ids]
    elif format=="shell":
        shell_ids = plotobject.arrays["element_shell_part_indexes"]
        part_numbers = part_ids[shell_ids]
    else:
        raise ValueError("element type not supported")
       
    
    return part_numbers


# function to find all elements belonging to a set of parts
def elements_in_part_set(
    element_part_ids: np.ndarray,
    part_list: list,
):
    '''
    Returns array of element indexes with dimension [n_elements_in_set,1]
    
    finds all elements associated with an array of part IDs
    '''
    # create list of element indexes which belong to part set
    mask = np.isin(element_part_ids, part_list)

    set_ids = np.where(mask)[0]

    return set_ids


# function to find all nodes associated with a part
def nodes_in_element_list(
    element_list: np.ndarray,
    element_indices: np.ndarray,
):
    '''
    Returns array of node indexes with dimension [n_nodes_in_set,1]
    
    finds all nodes associated with an array of part IDs
    '''
    element_nodes = element_indices[element_list]
    return np.unique(element_nodes)


# function to calculate the volume of a tetrahedron
def tetrahedron_volume(points: np.ndarray):
    '''
    Returns float volume
    
    Calculates the volume of the tetrahedron defined by the input points
    using the equation V=1/6*abs(det([points],[1,1,1,1]))
    '''
    
    det_matrix = np.vstack([np.transpose(points), [1, 1, 1, 1]])
    determinant = np.linalg.det(det_matrix)
    determinant = abs(determinant)
    volume = (1 / 6) * determinant
    return volume


# function to calculate the element volume for a given set of elements and nodes
def element_list_volume_history(
    element_indices: np.ndarray, node_coordinates: np.ndarray,
    type="solid",thickness=None
):
    '''
    Returns array of volumes for elements in a given set with 
    dimensions [n_timesteps,n_elements]
    
    Calculates the volume of each element using the scipy
    ConvexHull calculation to find the maximum possible volume
    given the 8 points of a hexahedral element
    '''
    #check valid input type and shell thickness
    if type == "shell" and thickness==None:
        raise ValueError("thickness must be specified for shell elements")
    elif type == "shell" and thickness != None:
        raise ValueError("shell element volume history not supported yet")
    elif type == "tshell":
        raise ValueError("tshell element volume history not supported yet")
    elif type == "solid":
        n_elements = element_indices.shape[0]
        if len(node_coordinates.shape) == 2:
            n_timesteps = 1
        else:
            n_timesteps = node_coordinates.shape[0]
        element_volume = np.zeros((n_timesteps, n_elements))

        element_nodes = node_coordinates[0, element_indices, :]
        hulls = np.array([sps.ConvexHull(nodes).volume for nodes in element_nodes])

        for i in range(1):
            element_volume[i, :] = hulls
    else:
        raise ValueError("type must be 'solid' or 'shell'")

    return element_volume





# function to calculate the volume fraction exceeding a threshold
# return: %>threshold
def volume_exceed(values: np.ndarray, volume: np.ndarray, threshold: float):
    # calculate total set volume
    vol_total = np.sum(volume)

    # find points that exceed threshold
    mask = values > threshold

    # calculate volume fraction from volume of mask
    vol_threshold = np.sum(volume[mask])
    vol_frac = vol_threshold / vol_total
    return vol_frac




'''
# function to process a file
def process_run(pathto: str, savepath: str, name: str):
    print(f"{datetime.now()}\tProcessing file {pathto}...")

    brain=brain_set()
    skull_shell, skull_solid = skull_sets()
    # brain=[101]
    # skull_shell=[101]
    # skull_solid=[101]

    process_start = time.time()

    print(f"{datetime.now()}\tLoading d3plot...")
    step_start = time.time()
    input_path = pathto + "d3plot"
    d3plot = D3plot(input_path, buffered_reading=True)
    # extract number of timesteps
    timesteps = d3plot.n_timesteps

    # define arrays of element and node ids
    element_solid_ids = d3plot.arrays["element_solid_ids"]
    element_shell_ids = d3plot.arrays["element_shell_ids"]
    element_solid_indices = d3plot.arrays["element_solid_node_indexes"]
    node_ids = d3plot.arrays["node_ids"]

    # create array of part IDs for each element
    element_solid_part_ids, element_shell_part_ids = element_part_ids(d3plot)
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")
    print(f"{datetime.now()}\tFinding elements in part sets...")
    step_start = time.time()
    # find all elements and nodes in given part list
    brain_elements = elements_in_part_set(element_solid_part_ids, brain)

    # calculate the nodal coordinate history
    node_history = d3plot.arrays["node_displacement"]
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    print(f"{datetime.now()}\tCalculating element volume history...")
    step_start = time.time()
    # calculate element volume history
    brain_volume_history = element_list_volume_history(
        element_solid_indices[brain_elements, :], node_history
    )
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    # calculate intracranial pressure
    print(f"{datetime.now()}\tCalculating pressure...")
    step_start = time.time()
    pressure = pressure(d3plot, brain_elements)
    pmaxtime = np.max(pressure, axis=0)
    p99 = np.quantile(pressure, 0.99, axis=0)
    p95 = np.quantile(pressure, 0.95, axis=0)

    pout = np.stack((pmaxtime, p99, p95), axis=1)
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    # calculate the principal and max shear strain
    print(f"{datetime.now()}\tCalculating principal strains...")
    step_start = time.time()
    prinstrain, msstrain = mps_mss(d3plot, brain_elements, "strain")
    psmaxtime = np.max(prinstrain[:, :, 0], axis=0)
    ps99 = np.quantile(prinstrain[:, :, 0], 0.99, axis=0)
    ps95 = np.quantile(prinstrain[:, :, 0], 0.95, axis=0)

    psout = np.stack((psmaxtime, ps99, ps95), axis=1)
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    # calculate the von mises stress
    print(f"{datetime.now()}\tCalculating von mises stresses...")
    step_start = time.time()
    vmstress = von_mises(d3plot, brain_elements)
    vmmaxtime = np.max(vmstress, axis=0)
    vm99 = np.quantile(vmstress, 0.99, axis=0)
    vm95 = np.quantile(vmstress, 0.95, axis=0)

    vmout = np.stack((vmmaxtime, vm99, vm95), axis=1)
    # print(vmstress[:,0])

    # print(vmstress[:,0])
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    print(f"{datetime.now()}\tCalculating part internal energy...")
    step_start = time.time()
    # calculate the internal energy
    inten = internal_energy(d3plot, skull_shell + skull_solid)
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    # Calculate CSDM and VSM metrics
    print(f"{datetime.now()}\tCalculating CSDM and VSM metrics...")
    step_start = time.time()
    csdm_matrix, csdm15, csdm25, vsm = csdm(prinstrain[:, :, 0], brain_volume_history)
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    print(f"{datetime.now()}\tWriting output files...")
    step_start = time.time()
    output_summary = [
        ["csdm15", csdm15],
        ["csdm25", csdm25],
        ["vsm", vsm],
        ["pressuremax", np.max(pmaxtime)],
        ["pressure99", np.max(p99)],
        ["pressure95", np.max(p95)],
        ["pstrainmax", np.max(psmaxtime)],
        ["pstrain99", np.max(ps99)],
        ["pstrain95", np.max(ps95)],
        ["vmemax", np.max(vmmaxtime)],
        ["vm99", np.max(vm99)],
        ["vm95", np.max(vm95)],
        ["skullenergy", np.max(inten)],
    ]

    summary_string = savepath + name + "_summary.csv"
    with open(summary_string, "w") as summaryfile:
        writer = csv.writer(summaryfile)
        writer.writerows(output_summary)

    # save outputs
    np.savetxt(savepath + name + "_pressure.csv", pressure, delimiter=",", fmt="%e")
    np.savetxt(savepath + name + "_pressurestats.csv", pout, delimiter=",", fmt="%e")
    np.savetxt(
        savepath + name + "_prinstrain.csv",
        prinstrain[:, :, 0],
        delimiter=",",
        fmt="%e",
    )
    np.savetxt(savepath + name + "_prinstrainstats.csv", psout, delimiter=",", fmt="%e")
    np.savetxt(savepath + name + "_Vonmises.csv", vmstress, delimiter=",", fmt="%e")
    np.savetxt(savepath + name + "_Vonmisesstats.csv", vmout, delimiter=",", fmt="%e")
    np.savetxt(
        savepath + name + "_CSDMhistory.csv", csdm_matrix, delimiter=",", fmt="%e"
    )

    process_end = time.time()
    step_end = time.time()
    print(f"{datetime.now()}\tComplete, {step_end-step_start} seconds.")

    print(
        f"{datetime.now()}\tFile processing complete for {pathto}, run time: {process_end-process_start} seconds"
    )


# ******************************MAIN*******************************

# load the d3plot file
pathto = "/scratch/jennings.t/fitimpact/expfront/"
outputpath = "/scratch/jennings.t/fitimpact/"
name = "expfront"


# pathto = "T:/LSDYNA/codetest/"
# outputpath = "T:/codes/THUMSinjurymetrics/"
# name = "codetest"
# pathto="T:\codes\THUMSinjurymetrics"

process_run(pathto, outputpath, name)
'''