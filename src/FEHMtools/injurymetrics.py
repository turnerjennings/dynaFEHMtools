from lasso.dyna import D3plot
import numpy as np

# function to calculate hydrostatic pressure
def element_pressure(object: D3plot, element_set: np.ndarray, type="solid"):
    '''
    Return array of float pressure with dimension [n_timesteps,n_elements]
    
    Calculates the hydrostatic pressure on each element in a given set for
    each timestep.
    Pressure is calculated from the stress tensor using p=1/3*tr(sigma).
    '''
    
    # load stress tensor from d3plot   
    if type == "solid":
        stress_tensor = object.arrays["element_solid_stress"]
    elif type == "shell":
        stress_tensor = object.arrays["element_shell_stress"]
    elif type == "tshell":
        stress_tensor = object.arrays["element_tshell_stress"]
    else:
        raise ValueError("Unrecognized element type")
        

    # filter stress tensor to objects of interest
    stress_tensor = stress_tensor[:, element_set, :, :]

    pressure = -(1 / 3) * (
        stress_tensor[:, :, :, 0]
        + stress_tensor[:, :, :, 1]
        + stress_tensor[:, :, :, 2]
    )

    pressure_element = np.sum(pressure, 2)
    return pressure_element


# function to calculate the max principal strain history
def mps_mss(object: D3plot, element_set: np.ndarray, stressstrain="stress",type="solid"):
    '''
    Returns an array of principal stresses or strains
    with demension [n_states,n_elements,3]
    Returns an array of max shear strain with shape [n_states,n_elements]

    for MPS array, values are sorted largest to smallest
    Principal confiuration calculated by the eigenvalues of the stress tensor
    '''
    if stressstrain == "strain" and type == "solid":
        ss_tensor = object.arrays["element_solid_strain"]
    elif stressstrain == "stress" and type == "solid":
        ss_tensor = object.arrays["element_solid_stress"]
    else:
        raise ValueError("Type must be 'stress' or 'strain'")

    ss_tensor = ss_tensor[:, element_set, :, :]
    # define strain tensor components
    sxx = ss_tensor[:, :, :, 0]
    syy = ss_tensor[:, :, :, 1]
    szz = ss_tensor[:, :, :, 2]
    sxy = ss_tensor[:, :, :, 3]
    syz = ss_tensor[:, :, :, 4]
    sxz = ss_tensor[:, :, :, 5]

    # calculate strain tensor
    tensor = np.array([[sxx, sxy, sxz], [sxy, syy, syz], [sxz, syz, szz]])
    tensor = np.sum(tensor, axis=4)

    eig_array = tensor.reshape(3, 3, -1)

    prinstrain = np.empty((3, eig_array.shape[2]))
    mss = np.empty((eig_array.shape[2]))

    for i in range(eig_array.shape[2]):
        eigs = np.linalg.eigvals(eig_array[:, :, i])
        eigs = eigs.flatten()
        prinstrain[:, i] = eigs
        mss[i] = 0.5 * (eigs[0] - eigs[2])
    prinstrain = prinstrain.reshape((3, tensor.shape[2], tensor.shape[3]))
    prinstrain = prinstrain.transpose(1, 2, 0)
    mss = mss.reshape((tensor.shape[2], tensor.shape[3]))

    return prinstrain, mss


# function to calculate the von mises stress
def von_mises(object: D3plot, element_set: np.ndarray):
    '''
    Returns an array of the von mises stress with dimension [n_states,n_elements]

    Calculates the von mises stress from the original stress tensor
    '''
    stress = object.arrays["element_solid_stress"]
    set_stress = stress[:, element_set, :, :]

    # calculate von mises stress
    vm = np.sqrt(
        (1 / 2)
        * (
            (set_stress[:, :, :, 0] - set_stress[:, :, :, 1])
            * (set_stress[:, :, :, 0] - set_stress[:, :, :, 1])
            + (set_stress[:, :, :, 1] - set_stress[:, :, :, 2])
            * (set_stress[:, :, :, 1] - set_stress[:, :, :, 2])
            + (set_stress[:, :, :, 2] - set_stress[:, :, :, 0])
            * (set_stress[:, :, :, 2] - set_stress[:, :, :, 0])
            + 6
            * (
                set_stress[:, :, :, 3] * set_stress[:, :, :, 3]
                + set_stress[:, :, :, 4] * set_stress[:, :, :, 4]
                + set_stress[:, :, :, 5] * set_stress[:, :, :, 5]
            )
        )
    )
    vm = np.squeeze(vm, axis=2)

    return vm


# function to return the internal energy of a part set
# return: array of part internal energy (n_states, n_parts)
def internal_energy(object: D3plot, partset: list):
    '''
    Returns the total internal energy of a part set

    Internal energy calculated from the sum of all parts in the given part set
    '''
    # find part index from part number
    ids = object.arrays["part_ids"]
    mask = np.isin(ids, partset)
    part_idx = np.where(mask)[0]

    # find internal energy from part index
    inten = object.arrays["part_internal_energy"]
    inten = np.sum(inten[:, part_idx], axis=1)
    return inten

# function to calculate the CSDM distribution
# return distribution, %>0.15, %>0.25
def csdm(MPS: np.ndarray, volume: np.ndarray):
    '''
    Return two floats of Cumulative Strain Damage Measure (CSDM)
    Return survival array with dimensions [1000]
    Return float of Volume Strain Metric

    CSDM15 and CSDM25 calculates the volume fraction of total unique 
    elements which exceed 0.15 and 0.25 strain respectively

    VSM calculates the area under the survival curve describing the 
    integral of volume-weighted strain
    '''
    # initialize outputs

    elmax = np.max(MPS, axis=0)
    thresholds = np.linspace(0, 0.5, 1000)
    v0 = volume[0, :].reshape(-1, 1)

    exceed = elmax[:, np.newaxis] > thresholds

    survival = np.sum(exceed * v0, axis=0) / np.sum(v0)

    csdm15 = survival[300]
    csdm25 = survival[500]

    VSM = np.trapz(survival, thresholds)
    return survival, csdm15, csdm25, VSM