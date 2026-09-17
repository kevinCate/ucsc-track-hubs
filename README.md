# ucsc-track-hubs

Independent, reusable collection of UCSC Genome Browser track hubs. Each
subfolder under `hg38/` is one project's tracks; the shared `hub.txt` /
`genomes.txt` / `hg38/trackDb.txt` at the repo root `include`s each project's
own `trackDb.txt` fragment, so there is exactly **one** hub URL to add in
UCSC no matter how many projects live here.

## This is an index, not a data store

Each `hg38/<project-slug>/` entry is a **symlink** into the source project
that generated it (e.g. `hg38/spi1-saturation-mutagenesis` ->
`/media/kevin/Bigdata3/Kevin/projects/playground/alphagenome/saturation_ism/results/SPI1/bigwig`).
The data isn't duplicated here; this repo just traces to where it actually
lives, so the source project stays self-contained and this repo stays small.

**Consequence for publishing:** git stores a symlink as a tiny text blob
containing the target path, not the file it points to. That's fine for local
use (a local web server or the desktop UCSC browser follows the symlink to
the real bytes), but **`git add`/`git push` of a symlink to a path outside
this repo will NOT carry the actual `.bw`/`trackDb.txt` bytes to GitHub** -
`raw.githubusercontent.com` would serve the tiny link-target string instead
of real bigWig data, and the hub would fail to load in the public browser.

Before pushing to GitHub, materialize real copies in place of the symlinks,
e.g. per project:
```bash
cd /media/kevin/Bigdata3/Kevin/projects/ucsc-track-hubs/hg38
rsync -L --delete -a spi1-saturation-mutagenesis/ .spi1-real/ \
  && rm spi1-saturation-mutagenesis && mv .spi1-real spi1-saturation-mutagenesis
```
(`rsync -L` dereferences the symlink and copies the real files.) Do this for
every project directory right before committing/pushing, or script it - this
repo doesn't do it automatically, since the whole point of the symlink is to
avoid needing a duplicate, always-in-sync copy for local/dev use.

## Using this hub in UCSC Genome Browser

1. Materialize real files as above, then push this repo to a public GitHub
   repository (or host it anywhere reachable over HTTP/HTTPS).
2. In UCSC Genome Browser: **My Data -> Track Hubs -> My Hubs** tab -> paste
   `https://raw.githubusercontent.com/<you>/<repo>/main/hub.txt` -> **Add Hub**.
   UCSC validates the hub on add and reports any errors inline.
3. Jump to a region (paste a gene symbol, or e.g. `chr11:47,329,859-47,403,547`
   for SPI1) - the composite tracks for every included project appear in the
   track list. Click a composite's label to toggle its sub-tracks or switch
   overlay/stacked display.

## Structure

```
hub.txt                  top-level hub definition
genomes.txt               -> hg38/trackDb.txt
hg38/
  trackDb.txt             `include`s every project below (auto-maintained)
  <project-slug>/         symlink -> the source project's own output dir
    trackDb.txt            this project's tracks (composite `multiWig` groups)
    *.bw                   the underlying signal files
```

## Adding a new project

Any future project can add itself here the same way: generate its own
self-contained `trackDb.txt` + `.bw` files in its own output directory, then
symlink `hg38/<project-slug>` to that directory, and add one line to
`hg38/trackDb.txt`:
```
include <project-slug>/trackDb.txt
```
No changes needed to `hub.txt`/`genomes.txt`, and no other project's tracks
are affected - composite track names are namespaced per project, so name
collisions across projects aren't a concern in practice.

The `saturation_ism` pipeline at
`/media/kevin/Bigdata3/Kevin/projects/playground/alphagenome/saturation_ism/`
does this automatically for every gene it processes - see its
`03_analyze_plot.py` (`link_hub_project()` / `write_hub_fragment()` /
`ensure_hub_root()`) and `config.HUB_ROOT` / `config.hub_symlink_path()`.

## Current projects

- `spi1-saturation-mutagenesis` -> SPI1 (PU.1) AlphaGenome Atlas saturation
  mutagenesis. Per hematopoietic cell type (CD34+ CMP, MPP, bone marrow
  tissue, bone marrow cell): mean SNV effect (signed) and strong-variant
  density (raw per-base, and 101bp-smoothed).
- `lamp2-saturation-mutagenesis` -> same, for LAMP2.
