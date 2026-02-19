#!/bin/bash
# Download audio from YouTube and convert to WAV

# Ensure deno is in PATH (required for yt-dlp)
export PATH="$HOME/.deno/bin:$PATH"

# Check if URL is provided as argument, otherwise use default
URL="${1:-https://www.youtube.com/watch?v=wOPNa-CZ99g}"
OUTPUT_NAME="${2:-volca}"

echo "Downloading audio from: $URL"
echo "Output file: ${OUTPUT_NAME}.wav"

# Download audio, trim to 30 seconds, and convert to WAV
# Using uv run to access yt-dlp in the project environment
uv run yt-dlp -f bestaudio \
  --extract-audio \
  --audio-format wav \
  --postprocessor-args "ffmpeg:-ss 0 -t 30" \
  --remote-components ejs:github \
  -o "${OUTPUT_NAME}.%(ext)s" \
  "$URL"

if [ $? -eq 0 ]; then
  echo "✅ Successfully downloaded: ${OUTPUT_NAME}.wav"
else
  echo "❌ Download failed. Try a different video URL:"
  echo "   Usage: ./download_audio_yt.sh <youtube-url> [output-name]"
  echo "   Example: ./download_audio_yt.sh 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' 'audio'"
  exit 1
fi
