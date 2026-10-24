#!/usr/bin/env bash
# Puts this case's input files in the working folder.
# files/home/ holds test state for ~/.founder (a made-up founder-context and logs).
# It is copied into $HOME only when EVAL_SANDBOX_HOME=1, so a rerun never touches your
# real ~/.founder by accident. Without it, the files land in ./.eval-home/ instead.
set -eu
here="$(dirname "$0")/files"
for item in "$here"/* "$here"/.[!.]*; do
  [ -e "$item" ] || continue
  [ "$(basename "$item")" = "home" ] && continue
  cp -R "$item" .
done
if [ -d "$here/home" ]; then
  if [ "${EVAL_SANDBOX_HOME:-0}" = "1" ]; then
    cp -R "$here/home/." "$HOME/"
  else
    mkdir -p .eval-home && cp -R "$here/home/." .eval-home/
  fi
fi
