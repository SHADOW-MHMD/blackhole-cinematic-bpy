#!/usr/bin/env python3
"""
Google Colab Headless GPU Renderer for The Anatomy of a Black Hole
==================================================================
Runs on Google Colab with NVIDIA T4 / V100 / A100 GPU acceleration.
Features:
- OptiX / CUDA GPU compute detection
- Automatic Google Drive checkpointing
- Resumption: skips frames that are already rendered
- Segmented batch rendering by Act or frame range
"""

import sys
import os
import argparse
import time

def setup_colab_paths():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    return repo_dir

repo_dir = setup_colab_paths()
import scene
import cinematics

def main():
    args = []
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]

    parser = argparse.ArgumentParser(description="Colab Black Hole GPU Batch Renderer")
    parser.add_argument("--start-frame", type=int, default=1, help="Starting frame number")
    parser.add_argument("--end-frame", type=int, default=cinematics.TOTAL_FRAMES, help="Ending frame number")
    parser.add_argument("--act", type=int, default=None, choices=[1, 2, 3, 4], help="Render specific Act (1, 2, 3, or 4)")
    parser.add_argument("--samples", type=int, default=96, help="Cycles samples per frame")
    parser.add_argument("--denoiser", type=str, default="AUTO", choices=["AUTO", "OPTIX", "OPENIMAGEDENOISE", "NONE"], help="Denoiser backend")
    parser.add_argument("--no-denoise", action="store_true", help="Disable denoising completely for pure raytrace speed")
    parser.add_argument("--drive-dir", type=str, default="/content/drive/MyDrive/blackhole_film/frames", help="Google Drive output directory")
    parser.add_argument("--local-dir", type=str, default="/content/frames", help="Local fast scratch directory")
    parser.add_argument("--resolution-percentage", type=int, default=100, help="Render resolution percent (100 = 1080p, 200 = 4K)")

    parsed = parser.parse_args(args)

    # Denoiser setting
    use_denoising = False if (parsed.no_denoise or parsed.denoiser == "NONE") else True
    denoiser_mode = "NONE" if not use_denoising else parsed.denoiser

    # Resolve frame range
    if parsed.act == 1:
        start_f, end_f = cinematics.ACT_TIMESTAMPS["ACT_1_START"], cinematics.ACT_TIMESTAMPS["ACT_1_END"]
    elif parsed.act == 2:
        start_f, end_f = cinematics.ACT_TIMESTAMPS["ACT_2_START"], cinematics.ACT_TIMESTAMPS["ACT_2_END"]
    elif parsed.act == 3:
        start_f, end_f = cinematics.ACT_TIMESTAMPS["ACT_3_START"], cinematics.ACT_TIMESTAMPS["ACT_3_END"]
    elif parsed.act == 4:
        start_f, end_f = cinematics.ACT_TIMESTAMPS["ACT_4_START"], cinematics.ACT_TIMESTAMPS["ACT_4_END"]
    else:
        start_f, end_f = parsed.start_frame, parsed.end_frame

    # Determine drive & local storage paths
    has_drive = os.path.exists("/content/drive/MyDrive")
    drive_dir = parsed.drive_dir if has_drive else None
    local_dir = parsed.local_dir
    os.makedirs(local_dir, exist_ok=True)
    if drive_dir:
        os.makedirs(drive_dir, exist_ok=True)

    print("==================================================================")
    print("  COLAB GPU BLACK HOLE RENDERER INITIALIZED")
    print(f"  Frame Range : {start_f} -> {end_f} (Total: {end_f - start_f + 1} frames)")
    print(f"  Samples     : {parsed.samples} (Cycles)")
    print(f"  Denoiser    : {denoiser_mode} (Active: {use_denoising})")
    print(f"  Fast Local  : {local_dir}")
    print(f"  Drive Sync  : {drive_dir if drive_dir else 'Disabled (Local only)'}")
    print("==================================================================")

    # Initialize scene
    scn = scene.generate_scene(samples=parsed.samples, use_denoising=use_denoising, denoiser=denoiser_mode)

    import bpy
    import shutil
    from concurrent.futures import ThreadPoolExecutor

    bpy.context.scene.render.resolution_percentage = parsed.resolution_percentage

    # Thread pool for non-blocking Google Drive sync
    drive_sync_pool = ThreadPoolExecutor(max_workers=2)

    def sync_to_drive(src, dst):
        try:
            shutil.copy2(src, dst)
        except Exception as err:
            print(f"[Drive Sync Warning] Could not copy {src} to {dst}: {err}")

    # Loop through frames with smart checkpointing
    rendered_count = 0
    skipped_count = 0
    t0 = time.time()

    total_frames = end_f - start_f + 1

    for f in range(start_f, end_f + 1):
        frame_filename = f"frame_{f:05d}.png"
        local_path = os.path.join(local_dir, frame_filename)
        drive_path = os.path.join(drive_dir, frame_filename) if drive_dir else None

        # Check if already rendered in Google Drive or local scratch
        if drive_path and os.path.exists(drive_path) and os.path.getsize(drive_path) > 1024:
            skipped_count += 1
            continue
        elif not drive_path and os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
            skipped_count += 1
            continue

        f_start = time.time()
        bpy.context.scene.frame_set(f)
        bpy.context.scene.render.filepath = local_path
        bpy.ops.render.render(write_still=True)
        f_dur = time.time() - f_start

        # Queue async sync to Google Drive
        if drive_path:
            drive_sync_pool.submit(sync_to_drive, local_path, drive_path)

        rendered_count += 1
        elapsed = time.time() - t0
        avg_speed = elapsed / max(1, rendered_count)
        remaining = (end_f - f) * avg_speed

        print(f"[{rendered_count}/{total_frames}] Frame {f:05d} rendered in {f_dur:.2f}s | Est. Remaining: {remaining/60:.1f}m")

    # Flush all pending drive sync jobs
    print("Waiting for all frames to sync to Google Drive...")
    drive_sync_pool.shutdown(wait=True)

    print(f"=== Rendering Complete! Rendered: {rendered_count}, Skipped (Already Completed): {skipped_count} ===")

if __name__ == "__main__":
    main()
