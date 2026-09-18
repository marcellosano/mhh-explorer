# Compound Europe — explorer for the compound-hazard results

Interactive explorer for *Compound climate hazard changes across Europe* (Sano, Ferrario, Torresan, Critto; manuscript in review). Static page plus data files; no server, no build step.

**Status: mockup v0.3, public preview.** The manuscript is under review. Please do not cite or redistribute numbers from this page until the paper is published; cite the paper once it is out.

Live page: https://marcellosano.github.io/mhh-explorer/

## Run locally

```
python3 -m http.server 8000
# open http://localhost:8000/
```

Opening `index.html` directly from disk will not work: the page fetches its data files, which browsers block over `file://`.

## Layout

- `index.html` — the page (single file, no dependencies)
- `spec.html` — the build specification
- `data/` — derived data read by the page (≈25 MB): compound occupancy grids per model × window × hazard, packed compound catalogues per hazard, single-hazard per-cell summaries (MPI-ESM1-2-HR), grid metadata, Natural Earth 110m coast and borders
- `build/` — the two scripts that produced `data/` from the pipeline outputs (`Outputs/Ensemble/raw_v2`) and the Phase-2 daily masks (Vault)

## Citation

Sano M., Ferrario D. M., Torresan S., Critto A. *Compound climate hazard changes across Europe*, manuscript in review (Nature Climate Change). Explorer: https://github.com/marcellosano/mhh-explorer. Data are derived products of ISIMIP3b (bias-adjusted GCM output) and the H08 hydrological model; the underlying ISIMIP data carry their own licence and citation requirements.

## Provenance

Pipeline: `mhh-compound-hazards` (this account). Data: ISIMIP3b, five GCMs (MPI-ESM1-2-HR, GFDL-ESM4, IPSL-CM6A-LR, MRI-ESM2-0, UKESM1-0-LL), 0.5°, Europe 35–70°N 15°W–40°E, 1981–2010 and 2031–2060 / 2071–2100 under SSP1-2.6, SSP3-7.0, SSP5-8.5. Thresholds frozen on 1981–2010; H08 socio-economic scenario 1850soc. Compound footprints are equal-area disks (centroid + extent), as in the paper.

Every number on the page is computed in the browser from the files in `data/`; nothing is typed in.
