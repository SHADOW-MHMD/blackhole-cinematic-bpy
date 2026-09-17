#!/usr/bin/env python3
"""
Procedural Gravitational Sound Design & Cinematic Atmosphere Generator
======================================================================
Synthesizes:
1. Sub-bass Infrasound Drone (32 Hz - 45 Hz modulated gravity wave)
2. Atmospheric Cosmic Chords (Interstellar-style pipe organ / string pads)
3. Relativistic Chirp (LIGO-style gravitational wave chirp sweep)
Outputs: /home/Mishal/bpy/audio/ambient_score_foley.wav (48kHz 24-bit stereo)
"""

import numpy as np
from scipy.io import wavfile
import os

SAMPLE_RATE = 48000
DURATION_SEC = 270  # 4 minutes 30 seconds
NUM_SAMPLES = int(SAMPLE_RATE * DURATION_SEC)

t = np.linspace(0, DURATION_SEC, NUM_SAMPLES, endpoint=False)

print(f"Synthesizing {DURATION_SEC}s cinematic audio track at {SAMPLE_RATE} Hz...")

# 1. Deep Gravitational Sub-Bass Drone (32 Hz with slow 0.05 Hz tidal breathing)
lfo_gravity = 0.5 + 0.5 * np.sin(2 * np.pi * 0.04 * t)
drone_32hz = np.sin(2 * np.pi * 32.7 * t) * 0.28 * lfo_gravity
drone_sub = np.sin(2 * np.pi * 16.35 * t) * 0.18 * lfo_gravity  # Infrasonic octaver

# 2. Ambient Harmonic Organ / String Pad (D minor cosmic progression: D - F - A - C)
# Base frequencies: D2 (73.4 Hz), A2 (110.0 Hz), D3 (146.8 Hz), F3 (174.6 Hz), C4 (261.6 Hz)
chord_d_min = (
    0.15 * np.sin(2 * np.pi * 73.41 * t) +
    0.12 * np.sin(2 * np.pi * 110.00 * t) +
    0.10 * np.sin(2 * np.pi * 146.83 * t) +
    0.08 * np.sin(2 * np.pi * 174.61 * t) +
    0.06 * np.sin(2 * np.pi * 220.00 * t)
)

# Slow volume envelope across the 4 Acts
env = np.zeros_like(t)
# Act 1 (0-60s): Quiet build
mask1 = (t >= 0) & (t < 60)
env[mask1] = np.linspace(0.1, 0.45, np.sum(mask1))

# Act 2 (60-150s): Majestic accretion roar
mask2 = (t >= 60) & (t < 150)
env[mask2] = 0.45 + 0.35 * np.sin(np.linspace(0, np.pi, np.sum(mask2)))

# Act 3 (150-225s): High-tension plunge to photon sphere
mask3 = (t >= 150) & (t < 225)
env[mask3] = np.linspace(0.8, 1.0, np.sum(mask3))

# Act 4 (225-270s): Cosmic resolution and fade
mask4 = (t >= 225) & (t <= 270)
env[mask4] = np.linspace(1.0, 0.02, np.sum(mask4))

pad_track = chord_d_min * env

# 3. Gravitational Wave Chirp during Act 3 plunge (around t = 195s to 215s)
chirp_track = np.zeros_like(t)
chirp_start = 195.0
chirp_end = 215.0
mask_chirp = (t >= chirp_start) & (t <= chirp_end)
t_chirp = t[mask_chirp] - chirp_start
tau = (chirp_end - chirp_start) - t_chirp + 0.05
f_chirp = 40.0 * (tau / 20.0)**(-3.0 / 8.0)
chirp_signal = np.sin(2 * np.pi * np.cumsum(f_chirp) / SAMPLE_RATE)
chirp_env = np.sin(np.linspace(0, np.pi, np.sum(mask_chirp)))
chirp_track[mask_chirp] = chirp_signal * chirp_env * 0.22

# Combine into Left and Right stereo channels with subtle phase width
left = drone_32hz + drone_sub + pad_track + chirp_track
right = drone_32hz + drone_sub + (pad_track * 0.98 + np.roll(pad_track, 240) * 0.02) + chirp_track

# Master Limiting / Normalization
stereo = np.vstack([left, right]).T
peak = np.max(np.abs(stereo))
if peak > 0:
    stereo = (stereo / peak) * 0.88  # -1.1 dB true peak headroom

# Convert to 16-bit PCM
audio_16bit = (stereo * 32767).astype(np.int16)

out_path = "/home/Mishal/bpy/audio/ambient_score_foley.wav"
wavfile.write(out_path, SAMPLE_RATE, audio_16bit)
print(f"Generated master audio stem: {out_path} ({os.path.getsize(out_path) / 1024 / 1024:.1f} MB)")
