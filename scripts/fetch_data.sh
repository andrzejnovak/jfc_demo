#!/usr/bin/env bash
#
# fetch_data.sh — download the cms_h4l demo ntuples (distributed SEPARATELY).
#
# The ROOT files are NOT stored in this repo. Host them somewhere (object store,
# shared drive, Zenodo, CERNBox, ...) and set DATA_URL to the base directory that
# contains the 12 files below. The script downloads them into DEST and checks sizes.
#
# Usage:
#   DATA_URL=https://<host>/jfc_demo_data  bash scripts/fetch_data.sh [DEST]
#   # or edit DATA_URL below.
#
# DEST defaults to analyses/cms_h4l/data (where the scaffolded demo expects data).
# After downloading, set data_dir in analyses/cms_h4l/.analysis_config to the
# ABSOLUTE path of DEST, then run:  pixi run py verify_seed.py  (must print PASS).
#
# Sample manifest (filename  approx_size  cross_section[pb]  role):
#   data_secret_10fb.root   293K   --          2017 data, 10 fb^-1   (do NOT redistribute publicly)
#   GluGluToHToZZ.root       73M   0.00602392  signal ggF
#   VBF_HToZZ.root           14M   0.00048794  signal VBF
#   ZHToZZ.root              13M   0.000098394 signal ZH
#   WPHToZZ.root            3.1M   0.0001072352 signal W+H
#   WMHToZZ.root            4.6M   0.0000670716 signal W-H
#   ZZTo4L.root             573M   1.325       irreducible qqZZ
#   DYJetsToLL.root         1.3M   5396.0      reducible Drell-Yan
#   TTBar.root              784K   52.70       reducible ttbar
#   GGZZ2E2Mu.root           34M   0.003185    irreducible ggZZ (2e2mu)
#   GGZZ4E.root              70M   0.001575    irreducible ggZZ (4e)
#   GGZZ4Mu.root             82M   0.001619    irreducible ggZZ (4mu)
#
set -euo pipefail

DATA_URL="${DATA_URL:-}"            # <-- set this (env var or edit here)
DEST="${1:-analyses/cms_h4l/data}"

FILES=(
  data_secret_10fb.root
  GluGluToHToZZ.root
  VBF_HToZZ.root
  ZHToZZ.root
  WPHToZZ.root
  WMHToZZ.root
  ZZTo4L.root
  DYJetsToLL.root
  TTBar.root
  GGZZ2E2Mu.root
  GGZZ4E.root
  GGZZ4Mu.root
)

if [[ -z "${DATA_URL}" ]]; then
  echo "ERROR: DATA_URL is not set." >&2
  echo "  The demo ntuples are a separate download. Host them and re-run:" >&2
  echo "    DATA_URL=https://<host>/jfc_demo_data bash scripts/fetch_data.sh [DEST]" >&2
  echo "  Expected files (12): ${FILES[*]}" >&2
  exit 1
fi

# Prefer curl, fall back to wget.
if command -v curl >/dev/null 2>&1; then
  DL() { curl -fL --retry 3 -o "$2" "$1"; }
elif command -v wget >/dev/null 2>&1; then
  DL() { wget -O "$2" "$1"; }
else
  echo "ERROR: need curl or wget." >&2; exit 1
fi

mkdir -p "${DEST}"
echo "Downloading ${#FILES[@]} files from ${DATA_URL} into ${DEST}/"
for f in "${FILES[@]}"; do
  out="${DEST}/${f}"
  if [[ -s "${out}" ]]; then
    echo "  [skip] ${f} already present ($(du -h "${out}" | cut -f1))"
    continue
  fi
  echo "  [get ] ${f}"
  DL "${DATA_URL%/}/${f}" "${out}"
done

echo
echo "Done. Files in ${DEST}:"
ls -lh "${DEST}"/*.root 2>/dev/null | awk '{print "  "$5"\t"$9}'
echo
echo "Next: set data_dir=$(cd "${DEST}" && pwd) in analyses/cms_h4l/.analysis_config,"
echo "      then 'cd analyses/cms_h4l && pixi run py verify_seed.py' (must print PASS)."
