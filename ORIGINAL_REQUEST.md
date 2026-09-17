# Original User Request

## 2026-09-16T17:04:10Z

A 4 to 5 minute Hollywood-grade, photorealistic 3D cinematic short film titled **"The Anatomy of a Black Hole: Accretion, Gravitational Lensing & The Event Horizon"**, built programmatically with Blender Python (`bpy`) and rendered via cloud GPU compute (Google Colab).

Working directory: /home/Mishal/bpy
Integrity mode: development

---

## Technical Directives & Research-First Policy

The team must conduct thorough research into existing open-source relativistic black hole shaders, OSL/GLSL implementations, Blender volumetric shader setups, and astrophysical models (e.g. Kip Thorne's equations from *Interstellar*, the Event Horizon Telescope data) before generating code. All code, scene setups, shaders, camera rigs, and rendering scripts must be cleanly organized inside `/home/Mishal/bpy`.

---

## Requirements

### R1. Scene Architecture & Relativistic Physics in `bpy`
- **Visual Spec**: 16:9 cinematic widescreen (2.39:1 letterbox), 24 fps, total runtime 4 to 5 minutes (~5,760 to 7,200 frames).
- **Physical Realism & Shaders**:
  - Procedural Kerr / Schwarzschild gravitational lensing shader in Blender that realistically warps background starfields, creating genuine Einstein rings and multiple image distortions.
  - Volumetric, turbulent accretion disk with Kelvin-Helmholtz fluid swirls, density waves, and realistic blackbody radiation (white-hot inner region transitioning to fiery orange, deep red, and dark outer dust).
  - Relativistic Doppler boosting: the approaching side of the accretion disk rotates toward the camera and is significantly brighter, hotter, and blue-shifted, while the receding side is dimmer and red-shifted.
  - The Event Horizon (.0 R_s$) rendered as an absolute black photon sink with a razor-sharp photon ring (.5 R_s$) where light orbits continuously.
- **Narrative Storyboard Across 4 Distinct Acts**:
  - **Act 1: The Approach (0:00 - 1:00)**: Drifting through deep-field star clusters; subtle gravitational micro-lensing warps distant galaxies as an invisible gravitational titan looms.
  - **Act 2: The Accretion Storm (1:00 - 2:30)**: Close orbital flyby revealing the roaring plasma accretion disk, relativistic beaming, magnetic field flux lines, and the glowing photon ring.
  - **Act 3: The Plunge to the Horizon (2:30 - 3:45)**: Dangerous descent toward the photon sphere; extreme optical warping, time dilation visual cues, and tidal gravity spaghettification physics.
  - **Act 4: The Singularity & Beyond (3:45 - 5:00)**: Passing the event horizon shadow, faint quantum Hawking radiation glow, and a breathtaking cosmic pullout revealing the monolithic structure in space.

### R2. Hollywood-Grade Audio & Soundscape
- **Orchestral Score**: Cinematic ambient orchestral music (Hans Zimmer *Interstellar* style — pipe organ chords, sweeping strings, slow atmospheric build).
- **Gravitational Sound Design**: Deep space gravitational foley (sub-bass infrasound rumbles, gravitational wave chirps, eerie vacuum resonance).
- **Narrator Voiceover**: Deep, authoritative, poetic yet scientifically rigorous narration timed across all 4 acts with cue sheets and audio processing instructions.

### R3. Google Colab Headless GPU Rendering Pipeline
- Automated Python execution scripts (`render_colab.py` or `.ipynb`) designed to run on Google Colab with GPU acceleration (NVIDIA T4 / V100 / A100).
- Cycles engine configured with OptiX / CUDA at 512+ samples per frame with volumetric ray bounces, motion blur, and depth-of-field.
- Chunked frame batching with Google Drive checkpointing so rendering resumes seamlessly across Colab timeouts.
- Local test rendering mode (1-frame preview, low-sample preview) for local verification before launching long cloud runs.

### R4. Final Assembly & Encoding
- Scripted FFmpeg assembly pipeline that takes rendered EXR/PNG image sequences, composites letterboxing, color grades (ACES / Filmic / AgX), mixes multi-track audio stems (narration, music, foley), and outputs the master 4K / 1080p MP4.

---

## Acceptance Criteria

### Code & Scene Verification
- [ ] `blender -b -P setup_blackhole.py` (or equivalent test script) runs headlessly and generates the complete procedural scene graph without errors.
- [ ] Test beauty frames for each Act (e.g. frames 500, 2000, 4000, 6000) render successfully with non-zero file sizes, valid colors, and correct gravitational lensing distortions.
- [ ] All shaders (lensing, accretion disk volume, photon sphere, starfield) compile cleanly in Blender Cycles.

### Pipeline & Automation
- [ ] A Google Colab notebook / runner script exists in `/home/Mishal/bpy` that can clone the repo, install Blender headlessly, mount Google Drive, and execute frame chunk rendering.
- [ ] An FFmpeg compilation script exists that combines rendered frames and audio tracks into a master MP4.

### Narrative & Audio
- [ ] A complete second-by-second narration and sound design script (`SCRIPT.md`) exists with timestamps spanning the full 4–5 minute runtime.
- [ ] Audio assets and generation guides are fully documented and integrated.
