# The Anatomy of a Black Hole: Accretion, Gravitational Lensing & The Event Horizon

A 4 to 5 minute Hollywood-grade, photorealistic 3D cinematic short film and scientific explainer, built programmatically using **Blender Python (`bpy`)** and rendered with **Cycles GPU compute** on **Google Colab**.

---

## 🌌 The 4 Acts

1. **Act 1: The Approach (0:00 – 1:00 | Frames 1 – 1440)**
   - Drifting through deep-field star clusters.
   - Subtle gravitational micro-lensing begins warping background galaxies.
   - Cinematic 55mm push-in with low-frequency gravitational infrasound.

2. **Act 2: The Accretion Storm (1:00 – 2:30 | Frames 1441 – 3600)**
   - Orbital flyby around the turbulent plasma accretion disk.
   - Relativistic Doppler boosting: the approaching side rotates toward the camera and is significantly brighter, hotter, and blue-shifted ($D \propto [\gamma(1 - \beta \cos \theta)]^{-3}$).
   - Gravitational lensing bends light from the far side over the top and bottom poles into dual glowing halos.

3. **Act 3: The Plunge to the Photon Sphere (2:30 – 3:45 | Frames 3601 – 5400)**
   - Dangerous descent toward the photon sphere ($1.5 R_s = 3.0 M$).
   - Crossing the Innermost Stable Circular Orbit (ISCO at $3.0 R_s = 6.0 M$).
   - Extreme optical warping where the universe compresses into an Einstein ring overhead.
   - Gravitational wave chirp resonance foley.

4. **Act 4: The Singularity & Beyond (3:45 – 4:30 | Frames 5401 – 6480)**
   - Skimming the event horizon shadow ($1.0 R_s = 2.0 M$).
   - Faint Hawking radiation thermal boundary.
   - Accelerating cosmic pullout revealing the monolithic scale against the eternal cosmos.

---

## 🔬 Relativistic Physics & Formulae

- **Schwarzschild Event Horizon**: $R_s = \frac{2GM}{c^2} = 2.0 M$
- **Photon Sphere**: $R_{ph} = 1.5 R_s = 3.0 M$
- **Apparent Shadow**: $b_{crit} = \sqrt{27} M \approx 5.196 M = 2.598 R_s$
- **ISCO**: $R_{ISCO} = 3.0 R_s = 6.0 M$
- **Doppler Factor**: $D = \frac{1}{\gamma (1 - \beta \cos \theta)}$
- **Shakura-Sunyaev Temperature**: $T(r) \propto \left(\frac{R_{ISCO}}{r}\right)^{3/4} \left(1 - \sqrt{\frac{R_{ISCO}}{r}}\right)^{1/4}$

---

## 🚀 How to Render on Google Colab (Free GPU)

1. Open **[Google Colab](https://colab.research.google.com/)**.
2. Select **Runtime -> Change runtime type -> T4 GPU / A100**.
3. Upload and open [`colab/Black_Hole_Cinematic_Colab.ipynb`](colab/Black_Hole_Cinematic_Colab.ipynb).
4. Run the cells:
   - **Cell 1**: Connects GPU and mounts Google Drive.
   - **Cell 2**: Installs Blender Linux 4.2 LTS in 15 seconds.
   - **Cell 3**: Clones or syncs project code.
   - **Cell 4**: Renders a single-frame preview (displays directly in the notebook).
   - **Cell 5**: Batch renders frames with OptiX GPU acceleration directly to your Google Drive.
   - **Cell 6**: Compiles the final video with audio using FFmpeg.

---

## 💻 Local CLI Usage

```bash
# Build and save .blend file:
blender -b -P build_scene.py -- --save-blend blackhole_master.blend

# Render a single test frame:
blender -b -P build_scene.py -- --render-frame 2000 --output output/preview_frame_2000.png

# Render a batch of frames locally:
blender -b -P build_scene.py -- --render-batch 1 240 --output-dir output/frames/

# Assemble frames + audio into master MP4:
./assemble_film.sh output/frames/ audio/ambient_score_foley.wav output/master.mp4
```

---

## 📁 Repository Structure

```
├── build_scene.py             # Main CLI runner for Blender
├── assemble_film.sh           # Master FFmpeg video/audio compilation script
├── README.md                  # Project documentation & science breakdown
├── src/
│   ├── astrophysics.py        # General relativity physics & metric constants
│   ├── shaders.py             # Procedural Cycles node-trees (disk, lensing, horizon)
│   ├── cinematics.py          # Camera paths, focal lengths, 4-act keyframing
│   └── scene.py               # Master procedural scene graph assembler
├── audio/
│   ├── script.md              # Complete 4.5-minute narration & sound cue sheet
│   ├── generate_foley.py      # Python gravitational wave & drone synthesizer
│   └── ambient_score_foley.wav# Synthesized master audio track (270s, 48kHz stereo)
└── colab/
    ├── render_colab.py        # Automated Colab headless GPU batch runner
    └── Black_Hole_Cinematic_Colab.ipynb # Interactive 1-click Colab notebook
```
