"""Small helpers for generating smooth random fields on a grid."""
from __future__ import annotations

import numpy as np
from scipy import ndimage


def gaussian_field(shape: tuple[int, int], dx: float, corr_m: float, rng: np.random.Generator) -> np.ndarray:
    """Zero-mean, unit-variance smooth random field (Gaussian filter of white noise).

    corr_m is the standard deviation of the smoothing kernel in metres; the resulting field has a
    Gaussian-shaped covariance with a range of roughly 2 * corr_m.
    """
    white = rng.standard_normal(shape)
    f = ndimage.gaussian_filter(white, sigma=max(corr_m / dx, 1e-6), mode="reflect")
    f -= f.mean()
    sd = f.std()
    return f / sd if sd > 0 else f


def distance_to(mask: np.ndarray, dx: float) -> np.ndarray:
    """Euclidean distance (m) from every cell to the nearest True cell of mask."""
    if not mask.any():
        return np.full(mask.shape, np.inf)
    return ndimage.distance_transform_edt(~mask) * dx
