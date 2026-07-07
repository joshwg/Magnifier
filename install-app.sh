#!/bin/sh
# Symlink ScreenMagnifier.app into ~/Applications (Launchpad/Spotlight/Dock).
# Idempotent; a symlink keeps the repo as the single source of truth.
# Named ScreenMagnifier to avoid clashing with the built-in macOS Magnifier.
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
DEST="$HOME/Applications"

mkdir -p "$DEST"
ln -sfn "$DIR/ScreenMagnifier.app" "$DEST/ScreenMagnifier.app"

echo "Linked $DEST/ScreenMagnifier.app -> $DIR/ScreenMagnifier.app"
echo "Look for \"ScreenMagnifier\" in Launchpad or Spotlight; drag it to the Dock to pin it."
