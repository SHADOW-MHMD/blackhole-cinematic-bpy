#!/usr/bin/env bash
set -e

FRAMES_DIR="${1:-output/frames}"
AUDIO_TRACK="${2:-audio/ambient_score_foley.wav}"
OUTPUT_MP4="${3:-output/The_Anatomy_of_a_Black_Hole_Cinematic.mp4}"

echo "=================================================================="
echo "  COMPILING FINAL MASTER FILM: THE ANATOMY OF A BLACK HOLE"
echo "  Frames Directory : $FRAMES_DIR"
echo "  Audio Track      : $AUDIO_TRACK"
echo "  Master Output    : $OUTPUT_MP4"
echo "=================================================================="

mkdir -p "$(dirname "$OUTPUT_MP4")"

# Check if frame sequence exists
FIRST_FRAME=$(find "$FRAMES_DIR" -name "*.png" | sort | head -n 1)
if [ -z "$FIRST_FRAME" ]; then
  echo "[Error] No PNG frames found in $FRAMES_DIR"
  exit 1
fi

echo "Found frame sequence starting at: $FIRST_FRAME"

# Detect naming pattern (e.g. frame_00001.png or frame_0001.png)
PATTERN="$FRAMES_DIR/frame_%05d.png"

# Execute FFmpeg master assembly
ffmpeg -y \
  -framerate 24 \
  -i "$PATTERN" \
  -i "$AUDIO_TRACK" \
  -c:v libx264 \
  -profile:v high \
  -preset slow \
  -crf 17 \
  -pix_fmt yuv420p \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -c:a aac \
  -b:a 320k \
  -shortest \
  -movflags +faststart \
  "$OUTPUT_MP4"

echo "=== Master Film Assembly Complete! ==="
ffprobe -v error -show_entries format=duration,size:stream=width,height,codec_name -of default=noprint_wrappers=1 "$OUTPUT_MP4"
