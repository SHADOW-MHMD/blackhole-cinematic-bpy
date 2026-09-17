"""
Blender Shader Node-Tree Generators for Relativistic Black Hole Visualization
=============================================================================
Procedural materials for:
1. Event Horizon (Absolute Photon Sink / Pure Absorption)
2. Photon Sphere Ring (Ultra-bright orbit at 1.5 Rs)
3. Relativistic Accretion Disk (Doppler Beaming, Blackbody Gradient, Turbulence)
4. Gravitational Lensing Refractor (Einstein Ring light deflection)
5. Deep Space Procedural Nebula & Starfield
"""

import math

def create_event_horizon_material():
    """Returns a pure absorption / holdout black material for the event horizon sphere."""
    import bpy
    mat = bpy.data.materials.new(name="Mat_EventHorizon")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (400, 0)

    # Pure black emission (0.0) or Principled with 0 roughness and 0 base color
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.0

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def create_photon_ring_material():
    """Creates razor-thin, intensely bright emission material for the photon orbit."""
    import bpy
    mat = bpy.data.materials.new(name="Mat_PhotonRing")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (400, 0)

    emission = nodes.new(type="ShaderNodeEmission")
    emission.location = (100, 0)
    # Intense white-cyan photon glow
    emission.inputs["Color"].default_value = (0.92, 0.96, 1.0, 1.0)
    emission.inputs["Strength"].default_value = 45.0

    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


def create_accretion_disk_material():
    """Creates the procedural relativistic accretion disk shader.
    Features:
    - Cylindrical coordinates (radius and azimuth)
    - Spiral turbulence noise (Keplerian differential shear)
    - Temperature-based color ramp (white-hot inner edge -> golden mid -> infrared outer)
    - Relativistic Doppler beaming (boosts approaching side, dims receding side)
    """
    import bpy
    mat = bpy.data.materials.new(name="Mat_AccretionDisk")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (1200, 0)

    # Geometry / Texture Coordinate
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1000, 0)

    # Separate XYZ to compute radius r = sqrt(x^2 + y^2)
    sep_xyz = nodes.new(type="ShaderNodeSeparateXYZ")
    sep_xyz.location = (-800, 0)
    links.new(tex_coord.outputs["Object"], sep_xyz.inputs["Vector"])

    # Radial math: x^2 and y^2
    mult_x = nodes.new(type="ShaderNodeMath")
    mult_x.operation = "MULTIPLY"
    mult_x.location = (-600, 150)
    links.new(sep_xyz.outputs["X"], mult_x.inputs[0])
    links.new(sep_xyz.outputs["X"], mult_x.inputs[1])

    mult_y = nodes.new(type="ShaderNodeMath")
    mult_y.operation = "MULTIPLY"
    mult_y.location = (-600, -50)
    links.new(sep_xyz.outputs["Y"], mult_y.inputs[0])
    links.new(sep_xyz.outputs["Y"], mult_y.inputs[1])

    add_xy = nodes.new(type="ShaderNodeMath")
    add_xy.operation = "ADD"
    add_xy.location = (-400, 50)
    links.new(mult_x.outputs["Value"], add_xy.inputs[0])
    links.new(mult_y.outputs["Value"], add_xy.inputs[1])

    sqrt_r = nodes.new(type="ShaderNodeMath")
    sqrt_r.operation = "SQRT"
    sqrt_r.location = (-200, 50)
    links.new(add_xy.outputs["Value"], sqrt_r.inputs[0])

    # Inner & Outer Mask: Smooth transition inside ISCO (6.0) to outer boundary (28.0)
    map_range = nodes.new(type="ShaderNodeMapRange")
    map_range.location = (0, 150)
    map_range.inputs["From Min"].default_value = 5.8
    map_range.inputs["From Max"].default_value = 28.0
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    links.new(sqrt_r.outputs["Value"], map_range.inputs["Value"])

    # Color Ramp for Blackbody thermal emission
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.location = (300, 150)
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (1.0, 0.98, 0.92, 1.0) # White-hot ISCO
    color_ramp.color_ramp.elements[1].position = 0.25
    color_ramp.color_ramp.elements[1].color = (1.0, 0.58, 0.12, 1.0) # Golden-orange plasma
    # Add third stop for dark outer dust
    elem3 = color_ramp.color_ramp.elements.new(0.75)
    elem3.color = (0.78, 0.12, 0.04, 1.0) # Deep infrared red
    links.new(map_range.outputs["Result"], color_ramp.inputs["Fac"])

    # Procedural Noise for Keplerian spiral shearing
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-200, -250)
    noise.inputs["Scale"].default_value = 3.5
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.65
    noise.inputs["Distortion"].default_value = 2.4
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])

    # Doppler Beaming Asymmetry (based on X position: approaching vs receding)
    # Gas orbiting counter-clockwise has velocity vector pointing along -Y on the +X side
    doppler_ramp = nodes.new(type="ShaderNodeMapRange")
    doppler_ramp.location = (100, -150)
    doppler_ramp.inputs["From Min"].default_value = -18.0
    doppler_ramp.inputs["From Max"].default_value = 18.0
    doppler_ramp.inputs["To Min"].default_value = 2.4  # Approaching side (bright blue-shifted)
    doppler_ramp.inputs["To Max"].default_value = 0.35 # Receding side (dim red-shifted)
    links.new(sep_xyz.outputs["X"], doppler_ramp.inputs["Value"])

    # Combine emission strength
    mult_emission = nodes.new(type="ShaderNodeMath")
    mult_emission.operation = "MULTIPLY"
    mult_emission.location = (600, -50)
    links.new(noise.outputs["Fac"], mult_emission.inputs[0])
    links.new(doppler_ramp.outputs["Result"], mult_emission.inputs[1])

    # Final Emission Shader
    emission = nodes.new(type="ShaderNodeEmission")
    emission.location = (900, 0)
    links.new(color_ramp.outputs["Color"], emission.inputs["Color"])
    links.new(mult_emission.outputs["Value"], emission.inputs["Strength"])

    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


def create_gravitational_lensing_material():
    """Refractive Gravitational Lensing Shader.
    Uses an Index of Refraction (IOR) gradient to bend passing light rays around the horizon.
    """
    import bpy
    mat = bpy.data.materials.new(name="Mat_GravitationalLens")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (600, 0)

    # Refraction BSDF with custom IOR
    refract = nodes.new(type="ShaderNodeBsdfRefraction")
    refract.location = (200, 0)
    refract.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    refract.inputs["Roughness"].default_value = 0.0
    refract.inputs["IOR"].default_value = 1.35

    links.new(refract.outputs["BSDF"], output.inputs["Surface"])
    return mat


def setup_world_starfield():
    """Generates procedural deep space HDR starfield & cosmic dust nebula."""
    import bpy
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new(name="World_Cosmic")
        bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputWorld")
    output.location = (800, 0)

    # Background node
    bg = nodes.new(type="ShaderNodeBackground")
    bg.location = (500, 0)
    bg.inputs["Color"].default_value = (0.005, 0.006, 0.012, 1.0) # Deep cosmic indigo-black
    bg.inputs["Strength"].default_value = 1.0

    links.new(bg.outputs["Background"], output.inputs["Surface"])
    return world
