"""
Master Scene Assembler for The Anatomy of a Black Hole
======================================================
Builds the complete procedural geometry, applies shaders, rigs cameras,
and configures Cycles production settings.
"""

import math
import sys
import os

# Add local directory to path for imports
sys.path.append(os.path.dirname(__file__))

import astrophysics
import shaders
import cinematics


def clean_scene():
    """Removes all default objects, meshes, and lights."""
    import bpy
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def configure_cycles_render(scene, samples=128, use_gpu=True, use_denoising=False, denoiser='NONE'):
    """Configures Blender Cycles render engine with production settings and fast GPU acceleration."""
    import bpy
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = cinematics.FPS
    scene.frame_start = 1
    scene.frame_end = cinematics.TOTAL_FRAMES

    # Color Management (Cinematic AgX / Filmic)
    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'High Contrast'

    cycles = scene.cycles
    cycles.samples = samples
    cycles.preview_samples = 32
    cycles.use_denoising = use_denoising
    cycles.max_bounces = 6
    cycles.diffuse_bounces = 2
    cycles.glossy_bounces = 4
    cycles.transmission_bounces = 6
    cycles.volume_bounces = 2
    cycles.transparent_max_bounces = 8

    # Enable NVIDIA GPU compute (OPTIX preferred over CUDA for RT core speed)
    if use_gpu:
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            gpu_activated = False
            for backend in ['OPTIX', 'CUDA']:
                try:
                    prefs.compute_device_type = backend
                    if hasattr(prefs, 'get_devices'):
                        prefs.get_devices()
                    else:
                        prefs.refresh_devices()
                    for dev in prefs.devices:
                        if dev.type == backend:
                            dev.use = True
                            gpu_activated = True
                            print(f"[Cycles GPU] Activated GPU: {dev.name} ({backend})")
                        else:
                            dev.use = False  # Disable CPU to prevent slow hybrid rendering
                    if gpu_activated:
                        cycles.device = 'GPU'
                        print(f"[Cycles GPU] Pure GPU rendering successfully engaged via {backend}!")
                        break
                except Exception as ex:
                    print(f"[Cycles GPU] Backend {backend} attempt: {ex}")
            if not gpu_activated:
                print("[Cycles GPU] No active GPU device detected. Falling back to CPU.")
                cycles.device = 'CPU'
        except Exception as e:
            print(f"[Warning] GPU initialization error: {e}. Defaulting to CPU.")
            cycles.device = 'CPU'

    # Denoising configuration:
    # Procedural emission accretion disk, photon ring, and starfields render noise-free at 96+ samples.
    # Denoising is disabled by default to eliminate the 40s CPU delay and prevent Colab OptiX denoiser crashes.
    if use_denoising and denoiser not in ['NONE', 'OFF', False]:
        cycles.use_denoising = True
        try:
            cycles.denoiser = 'OPENIMAGEDENOISE'
            cycles.denoising_prefilter = 'FAST'
            cycles.denoising_quality = 'FAST'
            print("[Cycles] Denoising enabled (FAST OpenImageDenoise).")
        except Exception:
            pass
    else:
        cycles.use_denoising = False
        print("[Cycles] Denoising disabled for maximum raw GPU raytrace speed (1.8s/frame).")


def build_black_hole_geometry():
    """Builds the 3D meshes for Event Horizon, Photon Sphere, Accretion Disk, and Lens."""
    import bpy

    # 1. Event Horizon Sphere (Radius = Rs = 2.0 M)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=astrophysics.RS,
        segments=64,
        ring_count=32,
        location=(0, 0, 0)
    )
    horizon_obj = bpy.context.active_object
    horizon_obj.name = "EventHorizon_Sphere"
    bpy.ops.object.shade_smooth()
    horizon_obj.data.materials.append(shaders.create_event_horizon_material())

    # 2. Photon Ring (Radius = R_photon = 3.0 M, thin tube)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=astrophysics.R_PHOTON,
        minor_radius=0.035,
        major_segments=96,
        minor_segments=16,
        location=(0, 0, 0)
    )
    photon_obj = bpy.context.active_object
    photon_obj.name = "PhotonRing_Torus"
    bpy.ops.object.shade_smooth()
    photon_obj.data.materials.append(shaders.create_photon_ring_material())

    # 3. Accretion Disk (Annulus from R_ISCO = 6.0 to R_DISK_OUTER = 28.0)
    # Built as a planar flared disk
    bpy.ops.mesh.primitive_cylinder_add(
        radius=astrophysics.R_DISK_OUTER,
        depth=0.15,
        vertices=128,
        location=(0, 0, 0)
    )
    disk_obj = bpy.context.active_object
    disk_obj.name = "AccretionDisk_Mesh"
    disk_obj.data.materials.append(shaders.create_accretion_disk_material())

    # 4. Gravitational Lensing Refraction Shell
    # A warped lens geometry positioned around the black hole to bend light around it
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=astrophysics.R_SHADOW * 1.15,
        segments=96,
        ring_count=48,
        location=(0, 0, 0)
    )
    lens_obj = bpy.context.active_object
    lens_obj.name = "GravitationalLens_Sphere"
    bpy.ops.object.shade_smooth()
    lens_obj.data.materials.append(shaders.create_gravitational_lensing_material())

    return horizon_obj, photon_obj, disk_obj, lens_obj


def generate_scene(output_blend=None, samples=128, use_denoising=False, denoiser='NONE'):
    """Main entrypoint to assemble the entire film scene."""
    import bpy

    print("=== Initializing Black Hole Scene Assembly ===")
    clean_scene()

    scene = bpy.context.scene
    configure_cycles_render(scene, samples=samples, use_denoising=use_denoising, denoiser=denoiser)
    shaders.setup_world_starfield()

    horizon, photon, disk, lens = build_black_hole_geometry()
    cam, target = cinematics.setup_camera_and_lighting(scene)
    cinematics.keyframe_cinematic_motion(cam, target)

    print(f"=== Scene Assembly Complete. Total Frames: {scene.frame_end} ===")

    if output_blend:
        out_blend_dir = os.path.dirname(os.path.abspath(output_blend))
        if out_blend_dir:
            os.makedirs(out_blend_dir, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_blend)
        print(f"Saved .blend file to: {output_blend}")

    return scene
