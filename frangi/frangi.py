import numpy as np

from .utils import divide_nonzero
from .hessian import absolute_hessian_eigenvalues


__all__ = ["frangi",
           "compute_measures",
           "compute_plate_like_factor",
           "compute_blob_like_factor",
           "compute_background_factor",
           "compute_vesselness",
           "filter_out_background"]


def frangi(nd_array, scale_range=(1, 10), scale_step=2, alpha=0.5, beta=0.5, frangi_c=500,
           black_vessels=True, estimate_frangi_c=True, debug=None):

    if not nd_array.ndim == 3:
        raise(ValueError("Only 3 dimensions is currently supported"))

    # from https://github.com/scikit-image/scikit-image/blob/master/skimage/filters/_frangi.py#L74
    sigmas = np.arange(scale_range[0], scale_range[1], scale_step)
    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    filtered_array = np.zeros(sigmas.shape + nd_array.shape)

    for i, sigma in enumerate(sigmas):
        eigenvalues, frangi_c_est = absolute_hessian_eigenvalues(
            nd_array, sigma=sigma, scale=True, estimate_frangi_c=estimate_frangi_c)

        if debug is not None:
            debug.disp(f"sigma {sigma}")
            debug.disp(f"eig1: {eigenvalues[0].min()} {eigenvalues[0].max()}")
            debug.disp(f"eig2: {eigenvalues[1].min()} {eigenvalues[1].max()}")
            debug.disp(f"eig3: {eigenvalues[2].min()} {eigenvalues[2].max()}")

            sigma_string = f"{sigma:.2f}".replace(".", "")
            debug.save_vector_mhd(f"eig_val_as_vec_{sigma_string}.mhd", "w", eigenvalues)

            debug.save_mhd(f"eig1_{sigma_string}.mhd", "w", eigenvalues[0])
            debug.save_mhd(f"eig2_{sigma_string}.mhd", "w", eigenvalues[1])
            debug.save_mhd(f"eig3_{sigma_string}.mhd", "w", eigenvalues[2])

        if estimate_frangi_c:
            frangi_c = frangi_c_est

        filtered_array[i] = compute_vesselness(*eigenvalues, alpha=alpha, beta=beta, c=frangi_c,
                                               black_white=black_vessels, debug=debug, sigma=sigma)

    return np.max(filtered_array, axis=0)


def compute_measures(eigen1, eigen2, eigen3):
    """
    RA - plate-like structures
    RB - blob-like structures
    S - background
    """
    Ra = divide_nonzero(np.abs(eigen2), np.abs(eigen3))
    Rb = divide_nonzero(np.abs(eigen1), np.sqrt(np.abs(np.multiply(eigen2, eigen3))))
    S = np.sqrt(np.square(eigen1) + np.square(eigen2) + np.square(eigen3))
    return Ra, Rb, S


def compute_plate_like_factor(Ra, alpha):
    return 1 - np.exp(np.negative(np.square(Ra)) / (2 * np.square(alpha)))


def compute_blob_like_factor(Rb, beta):
    return np.exp(np.negative(np.square(Rb) / (2 * np.square(beta))))


def compute_background_factor(S, c):
    return 1 - np.exp(np.negative(np.square(S)) / (2 * np.square(c)))


def compute_vesselness(eigen1, eigen2, eigen3, alpha, beta, c, black_white, debug=None, sigma=0):
    Ra, Rb, S = compute_measures(eigen1, eigen2, eigen3)
    plate = compute_plate_like_factor(Ra, alpha)
    blob = compute_blob_like_factor(Rb, beta)
    background = compute_background_factor(S, c)


    if debug is not None:
        debug.disp(f"Ra: {Ra.min():.2f} {Ra.max():.2f}")
        debug.disp(f"Rb: {Rb.min():.2f} {Rb.max():.2f}")
        debug.disp(f"S: {S.min():.2f} {S.max():.2f}")
        debug.disp(f"plate: {plate.min():.2f} {plate.max():.2f}")
        debug.disp(f"blob: {blob.min():.2f} {blob.max():.2f}")
        debug.disp(f"background: {background.min():.2f} {background.max():.2f}")
        debug.push_subdir("vesselness")
        sigma_string = f"{sigma:.2f}".replace(".", "")
        debug.save_mhd(f"plate_Ra_1_s{sigma_string}.mhd", "w", plate)
        debug.save_mhd(f"blob_Rb_1_s{sigma_string}.mhd", "w", blob)
        debug.save_mhd(f"background_S_1_s{sigma_string}.mhd", "w", background)
        debug.save_mhd(f"Ra_1_s{sigma_string}.mhd", "w", Ra)
        debug.save_mhd(f"Rb_1_s{sigma_string}.mhd", "w", Rb)
        debug.save_mhd(f"S_1_s{sigma_string}.mhd", "w", S)
        debug.disp(f"alpha {alpha} beta {beta} c {c}")
        debug.pop_subdir()

    return filter_out_background(plate * blob * background, black_white, eigen2, eigen3)


def filter_out_background(voxel_data, black_white, eigen2, eigen3):
    """
    Set black_white to true if vessels are darker than the background and to false if
    vessels are brighter than the background.
    """
    if black_white:
        voxel_data[eigen2 < 0] = 0
        voxel_data[eigen3 < 0] = 0
    else:
        voxel_data[eigen2 > 0] = 0
        voxel_data[eigen3 > 0] = 0
    voxel_data[np.isnan(voxel_data)] = 0
    return voxel_data
