"""
Camera Choreography, Lighting, and Act Timeline Animation
=========================================================
Defines the cinematic camera paths, focal lengths, depth-of-field, and
animation keyframing across the 4 acts.
"""

import math

FPS = 24
TOTAL_FRAMES = 6480  # 4 minutes 30 seconds @ 24 fps

ACT_TIMESTAMPS = {
    "ACT_1_START": 1,
    "ACT_1_END": 1440,    # 0:00 - 1:00 (The Approach)
    "ACT_2_START": 1441,
    "ACT_2_END": 3600,    # 1:00 - 2:30 (The Accretion Storm)
    "ACT_3_START": 3601,
    "ACT_3_END": 5400,    # 2:30 - 3:45 (The Plunge to the Photon Sphere)
    "ACT_4_START": 5401,
    "ACT_4_END": 6480,    # 3:45 - 4:30 (The Singularity & Cosmic Pullout)
}


def setup_camera_and_lighting(scene):
    """Creates the master cinema camera and rigs it with target tracking."""
    import bpy

    # Create camera
    cam_data = bpy.data.cameras.new(name="CinemaCamera")
    cam_data.lens = 45.0  # 45mm cinema prime
    cam_data.sensor_width = 36.0  # Full frame 35mm
    cam_data.clip_start = 0.1
    cam_data.clip_end = 2000.0

    # Depth of field
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 2.8

    cam_obj = bpy.data.objects.new(name="CinemaCamera_Obj", object_data=cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Create focus target at Black Hole center
    target = bpy.data.objects.new(name="CamTarget_Center", object_data=None)
    target.location = (0.0, 0.0, 0.0)
    scene.collection.objects.link(target)
    cam_data.dof.focus_object = target

    # Track to constraint
    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    return cam_obj, target


def keyframe_cinematic_motion(cam_obj, target):
    """Keyframes the camera trajectory across all 4 acts."""
    import bpy

    cam_data = cam_obj.data

    # --- ACT 1: The Cosmic Approach (Frames 1 - 1440) ---
    # Start far back in deep space, high inclination
    cam_obj.location = (0.0, -68.0, 18.0)
    cam_data.lens = 55.0
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_data.keyframe_insert(data_path="lens", frame=1)

    # Midway through approach: subtle lateral drift
    cam_obj.location = (8.0, -42.0, 10.0)
    cam_data.lens = 50.0
    cam_obj.keyframe_insert(data_path="location", frame=720)
    cam_data.keyframe_insert(data_path="lens", frame=720)

    # End of Act 1: Entering the gravitational influence zone
    cam_obj.location = (14.0, -28.0, 6.0)
    cam_data.lens = 45.0
    cam_obj.keyframe_insert(data_path="location", frame=1440)
    cam_data.keyframe_insert(data_path="lens", frame=1440)

    # --- ACT 2: The Accretion Storm (Frames 1441 - 3600) ---
    # Orbital sweeping pass around the turbulent accretion disk
    num_orbital_points = 6
    act2_duration = 3600 - 1440
    for i in range(num_orbital_points + 1):
        frac = i / float(num_orbital_points)
        frame = int(1440 + frac * act2_duration)
        theta = frac * 1.6 * math.pi + 0.3
        radius = 26.0 - frac * 8.0  # Spiral inward from r=26 to r=18
        z_height = 4.5 * math.cos(frac * math.pi) + 2.0  # Gentle vertical wave

        cam_obj.location = (radius * math.cos(theta), radius * math.sin(theta), z_height)
        cam_obj.keyframe_insert(data_path="location", frame=frame)

    # --- ACT 3: The Plunge to the Photon Sphere (Frames 3601 - 5400) ---
    # Fast, intense diving shot straight toward the photon ring
    cam_obj.location = (12.0, -12.0, 3.5)
    cam_data.lens = 32.0  # Widen field of view
    cam_obj.keyframe_insert(data_path="location", frame=3601)
    cam_data.keyframe_insert(data_path="lens", frame=3601)

    # Grazing the photon sphere at r = 3.6 (just above 3.0 M)
    cam_obj.location = (3.2, -2.4, 0.6)
    cam_data.lens = 24.0  # Ultra-wide
    cam_obj.keyframe_insert(data_path="location", frame=4600)
    cam_data.keyframe_insert(data_path="lens", frame=4600)

    cam_obj.location = (2.2, -1.8, 0.2)
    cam_obj.keyframe_insert(data_path="location", frame=5400)

    # --- ACT 4: The Singularity & Cosmic Pullout (Frames 5401 - 6480) ---
    # Skimming the event horizon edge, then pulling back exponentially
    cam_obj.location = (0.0, -3.5, 0.1)
    cam_data.lens = 35.0
    cam_obj.keyframe_insert(data_path="location", frame=5401)
    cam_data.keyframe_insert(data_path="lens", frame=5401)

    # Massive accelerating cosmic pullout
    cam_obj.location = (0.0, -85.0, 24.0)
    cam_data.lens = 65.0
    cam_obj.keyframe_insert(data_path="location", frame=6480)
    cam_data.keyframe_insert(data_path="lens", frame=6480)

    # Set interpolation to smooth bezier on all curves
    if cam_obj.animation_data and cam_obj.animation_data.action:
        for fcurve in cam_obj.animation_data.action.fcurves:
            for kfp in fcurve.keyframe_points:
                kfp.interpolation = "BEZIER"
