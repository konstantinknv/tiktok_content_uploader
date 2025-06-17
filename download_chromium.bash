#!/bin/bash
set -e

CHROMIUM_URL="https://github.com/macchrome/linchrome/releases/download/v136.7103.97-M136.0.7103.97-r1440670-portable-ungoogled-Lin64/ungoogled-chromium_136.0.7103.97_1.vaapi_linux.tar.gz"
OUTPUT="chromium.tar.gz"
DIR="./chromium"

echo "Downloading Chromium..."
curl --fail -L -o "$OUTPUT" "$CHROMIUM_URL"

mkdir -p "$DIR"

echo "Extracting Chromium..."
tar -xzf "$OUTPUT" -C "$DIR"

rm "$OUTPUT"

echo "Chromium downloaded and extracted to '$DIR'."