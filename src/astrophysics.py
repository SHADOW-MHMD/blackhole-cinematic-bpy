"""
Astrophysical Constants and Relativistic Physics for Black Hole Visualization
=============================================================================
Formulas based on general relativity (Schwarzschild & Kerr metrics) and
standard Shakura-Sunyaev thin/thick accretion disk theory.
"""

import math

# Geometric units where G = c = 1, Mass M = 1
M = 1.0

# Critical Radii (Schwarzschild Metric)
RS = 2.0 * M                   # Schwarzschild Event Horizon radius: r_s = 2GM/c^2 = 2.0
R_PHOTON = 1.5 * RS            # Photon Sphere radius: r_ph = 3M = 1.5 r_s = 3.0
R_ISCO = 3.0 * RS              # Innermost Stable Circular Orbit: r_isco = 6M = 3.0 r_s = 6.0
R_SHADOW = math.sqrt(27.0) * M # Apparent shadow radius as seen from infinity: b_crit = sqrt(27) M ≈ 5.196 M = 2.598 r_s

# Outer Disk Extent (in units of M)
R_DISK_INNER = R_ISCO          # Inner accretion boundary at ISCO (6.0 M)
R_DISK_OUTER = 32.0 * M        # Outer dust boundary (32.0 M = 16 r_s)
DISK_SCALE_HEIGHT = 0.08       # Disk thickness aspect ratio h/r ≈ 0.08 (semi-thin flaring disk)


def keplerian_velocity(r):
    """Orbital velocity of gas in circular orbit around Schwarzschild black hole.
    v/c = sqrt(M / (r - 2M)) for proper frame, or coordinate v/c = sqrt(M / r).
    """
    if r <= RS:
        return 1.0  # Light-speed at horizon
    return math.sqrt(M / r)


def gravitational_redshift_factor(r):
    """Gravitational time dilation / redshift factor:
    g_grav = sqrt(1 - 2M / r) = sqrt(1 - r_s / r).
    At r -> infinity, g -> 1.0. At r -> r_s, g -> 0.0 (infinite redshift).
    """
    if r <= RS:
        return 0.0
    return math.sqrt(max(0.0, 1.0 - RS / r))


def relativistic_doppler_factor(r, view_angle_rad):
    """Relativistic Doppler beaming factor for gas moving toward/away from observer:
    D = 1 / (gamma * (1 - beta * cos(theta)))
    where beta = v/c, gamma = 1 / sqrt(1 - beta^2).
    """
    v = keplerian_velocity(r)
    beta = min(0.999, v)
    gamma = 1.0 / math.sqrt(max(0.001, 1.0 - beta**2))
    cos_theta = math.cos(view_angle_rad)
    doppler_shift = 1.0 / (gamma * (1.0 - beta * cos_theta))
    return doppler_shift


def accretion_disk_temperature(r, T_max=1.0):
    """Shakura-Sunyaev temperature profile:
    T(r) ~ T_max * (r_isco / r)^(3/4) * (1 - sqrt(r_isco / r))^(1/4)
    Returns normalized temperature [0.0, 1.0].
    """
    if r < R_ISCO:
        return 0.0
    ratio = R_ISCO / r
    # Peak temperature occurs at r ≈ 1.36 r_isco (approx 8.16 M)
    t_profile = (ratio**0.75) * max(0.0, 1.0 - math.sqrt(ratio))**0.25
    # Normalize so max is roughly 1.0 (raw peak is ~ 0.488)
    return min(1.0, (t_profile / 0.488) * T_max)


def einstein_deflection_angle(b):
    """Light deflection angle alpha(b) for impact parameter b:
    In weak field (b >> M): alpha ≈ 4M / b
    Near photon sphere (b -> b_crit): alpha diverges logarithmically:
    alpha(b) ~ -ln(b / b_crit - 1) + const
    """
    if b <= R_SHADOW:
        return math.pi * 2.0  # Captured into horizon
    if b > 4.0 * R_SHADOW:
        return (4.0 * M) / b
    x = (b - R_SHADOW) / M
    if x <= 0:
        return math.pi * 2.0
    return min(math.pi * 2.0, -math.log(min(1.0, x / 1.5)) * 0.8 + (4.0 * M) / b)
