#!/usr/bin/env python3
"""Structural pre-flight check for this hub, no network/UCSC needed.

Checks hub.txt/genomes.txt/trackDb.txt required keys, that every `include`
resolves, and that every `bigDataUrl` points at a real, non-empty file
(following symlinks) - the same class of error UCSC's own hub validator
flags on "Add Hub", just catchable locally first.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
errors = []
warnings = []


def require(path: pathlib.Path, keys: list[str], label: str) -> dict:
  if not path.exists():
    errors.append(f'{label}: missing {path}')
    return {}
  kv = {}
  for line in path.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
      continue
    parts = line.split(None, 1)
    if len(parts) == 2:
      kv[parts[0]] = parts[1]
  for k in keys:
    if k not in kv:
      errors.append(f'{label}: {path} missing required key "{k}"')
  return kv


hub = require(ROOT / 'hub.txt', ['hub', 'shortLabel', 'longLabel', 'genomesFile'], 'hub.txt')
genomes = require(ROOT / 'genomes.txt', ['genome', 'trackDb'], 'genomes.txt')

if genomes.get('trackDb'):
  top_trackdb = ROOT / genomes['trackDb']
  if not top_trackdb.exists():
    errors.append(f'genomes.txt: trackDb target missing: {top_trackdb}')
  else:
    n_tracks = 0
    for m in re.finditer(r'^include\s+(\S+)', top_trackdb.read_text(), re.M):
      frag = top_trackdb.parent / m.group(1)
      if not frag.exists():
        errors.append(f'{top_trackdb}: include target missing: {frag}')
        continue
      text = frag.read_text()
      track_names = re.findall(r'^\s*track\s+(\S+)', text, re.M)
      if len(track_names) != len(set(track_names)):
        dupes = {t for t in track_names if track_names.count(t) > 1}
        errors.append(f'{frag}: duplicate track name(s): {sorted(dupes)}')
      for bd in re.finditer(r'^\s*bigDataUrl\s+(\S+)', text, re.M):
        bw = frag.parent / bd.group(1)
        if not bw.exists():
          errors.append(f'{frag}: bigDataUrl target missing: {bw}')
        elif bw.stat().st_size == 0:
          errors.append(f'{frag}: bigDataUrl target is empty: {bw}')
        else:
          n_tracks += 1
    print(f'Checked {n_tracks} bigDataUrl track file(s) across '
          f'{len(list(re.finditer(r"^include", top_trackdb.read_text(), re.M)))} '
          f'included project(s).')

for w in warnings:
  print(f'WARNING: {w}')
if errors:
  print(f'\n{len(errors)} ERROR(S):')
  for e in errors:
    print(f'  - {e}')
  sys.exit(1)
print('OK: hub structure looks valid.')
