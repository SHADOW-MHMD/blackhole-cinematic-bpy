#!/usr/bin/env python3
"""
CLI Runner for building and rendering the Black Hole Cinematic film
Usage:
    blender -b -P build_scene.py -- --save-blend blackhole.blend
    blender -b -P build_scene.py -- --render-frame 500 --output preview_500.png
    blender -b -P build_scene.py -- --render-batch 1 500 --output-dir //output/frames/
"""

import sys
import os
import argparse

# Add src to python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import scene

def main():
    # Parse arguments after '--'
    args = []
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]

    parser = argparse.ArgumentParser(description="Black Hole Blender Builder")
    parser.add_argument("--save-blend", type=str, default=None, help="Path to save .blend file")
    parser.add_argument("--samples", type=int, default=128, help="Cycles render samples")
    parser.add_argument("--denoiser", type=str, default="NONE", choices=["NONE", "OPENIMAGEDENOISE"], help="Denoiser backend")
    parser.add_argument("--denoise", action="store_true", help="Enable denoising")
    parser.add_argument("--no-denoise", action="store_true", help="Explicitly disable denoising (default)")
    parser.add_argument("--render-frame", type=int, default=None, help="Render a single frame")
    parser.add_argument("--render-batch", nargs=2, type=int, default=None, help="Render frame range: start end")
    parser.add_argument("--output", type=str, default="output/preview.png", help="Output path for single frame render")
    parser.add_argument("--output-dir", type=str, default="output/frames/", help="Output directory for batch frames")

    parsed = parser.parse_args(args)

    use_denoising = False
    if parsed.denoise or (parsed.denoiser != "NONE"):
        use_denoising = True
    if parsed.no_denoise:
        use_denoising = False
    denoiser_mode = parsed.denoiser if use_denoising else "NONE"

    # Build scene
    scn = scene.generate_scene(output_blend=parsed.save_blend, samples=parsed.samples, use_denoising=use_denoising, denoiser=denoiser_mode)

    import bpy

    if parsed.render_frame is not None:
        out_dir = os.path.dirname(os.path.abspath(parsed.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        bpy.context.scene.frame_set(parsed.render_frame)
        bpy.context.scene.render.filepath = parsed.output
        print(f"Rendering single frame {parsed.render_frame} to {parsed.output}...")
        bpy.ops.render.render(write_still=True)
        print(f"Render complete: {parsed.output}")

    elif parsed.render_batch is not None:
        start, end = parsed.render_batch
        os.makedirs(parsed.output_dir, exist_ok=True)
        bpy.context.scene.render.filepath = os.path.join(parsed.output_dir, "frame_######")
        bpy.context.scene.frame_start = start
        bpy.context.scene.frame_end = end
        print(f"Rendering batch frames {start} to {end} to {parsed.output_dir}...")
        bpy.ops.render.render(animation=True)
        print(f"Batch render complete.")

if __name__ == "__main__":
    main()
