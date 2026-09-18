"""Occupancy grids (days/yr under a compound event) for every GCM x hazard x window, plus packed compound catalogues.
Reads Outputs/Ensemble/raw_v2/<gcm>/Phase4_Footprints_v2/multihazard_<h>.csv; writes JSON into the scratchpad only."""
import pandas as pd, numpy as np, json, sys, pathlib, time
D = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
RAW = D/"Outputs/Ensemble/raw_v2"
cells = pd.read_csv(D/"Outputs/v2_analyses/spatial_shift/spatial_shift_cells.csv")
land = cells[cells.hazard == "heat_drought_fire"][["lat", "lon", "is_land"]]
lats = np.sort(land.lat.unique()); lons = np.sort(land.lon.unique()); LON, LAT = np.meshgrid(lons, lats)
landm = np.zeros(LON.shape, bool)
for r in land.itertuples(): landm[np.searchsorted(lats, r.lat), np.searchsorted(lons, r.lon)] = bool(r.is_land)
kmlat = 111.0; kmlon = 111.0 * np.cos(np.deg2rad(LAT))
GCMS = ["mpi", "gfdl", "ipsl", "mri", "ukesm"]; HZ = ["heat_drought_fire", "flood", "windstorm"]
WINDOWS = [("hist", "historical", 1981, 2010)] + [(f"{s}_{w}", s, y0, y1) for s in ["ssp126", "ssp370", "ssp585"] for w, y0, y1 in [("mid", 2031, 2060), ("late", 2071, 2100)]]
def occupancy(df):
    g = np.zeros(LON.shape); n = np.zeros(LON.shape)
    for e in df.itertuples():
        rad = np.sqrt(e.spatial_extent_km2 / np.pi)
        m = np.sqrt(((LAT - e.center_lat) * kmlat) ** 2 + ((LON - e.center_lon) * kmlon) ** 2) <= rad
        g[m] += e.duration_days; n[m] += 1
    return g, n
grids = {"lat": lats.tolist(), "lon": lons.tolist(), "land": landm.astype(int).flatten().tolist(), "windows": [w[0] for w in WINDOWS], "gcms": GCMS, "hazards": HZ, "days": {}, "count": {}}
cat = {}
t0 = time.time()
for h in HZ:
    for g in GCMS:
        d = pd.read_csv(RAW/g/"Phase4_Footprints_v2"/f"multihazard_{h}.csv"); d["year"] = pd.to_datetime(d.start_day).dt.year; d["doy"] = pd.to_datetime(d.start_day).dt.dayofyear
        for key, scen, y0, y1 in WINDOWS:
            sub = d[(d.scenario == scen) & (d.year >= y0) & (d.year <= y1)]
            days, cnt = occupancy(sub)
            grids["days"][f"{h}|{g}|{key}"] = np.round(days[landm] / 30.0, 2).tolist()
            grids["count"][f"{h}|{g}|{key}"] = np.round(cnt[landm] / 30.0, 3).tolist()
        # packed catalogue (columnar) for client-side filtering
        wk = np.full(len(d), "", dtype=object)
        for key, scen, y0, y1 in WINDOWS: wk[(d.scenario == scen) & (d.year >= y0) & (d.year <= y1)] = key
        keep = wk != ""; dd = d[keep]
        cat[f"{h}|{g}"] = {
            "w": [grids["windows"].index(k) for k in wk[keep]],
            "y": dd.year.tolist(), "doy": dd.doy.tolist(), "dur": dd.duration_days.tolist(),
            "lat": np.round(dd.center_lat, 2).tolist(), "lon": np.round(dd.center_lon, 2).tolist(),
            "km2": np.round(dd.spatial_extent_km2, -2).astype(int).tolist(),
            "sev": np.round(dd.exceed_sum, 1).tolist(), "int": np.round(dd.exceed_mean, 3).tolist(),
            "ncond": dd.n_conditioning_hazards.tolist(),
            "hum": dd["has_low_humidity"].astype(int).tolist() if "has_low_humidity" in dd else [], "soil": dd["has_dry_soil"].astype(int).tolist() if "has_dry_soil" in dd else [], "pdef": dd["has_precip_deficit"].astype(int).tolist() if "has_precip_deficit" in dd else [],
        }
        print(f"{h} {g} events {len(dd)}  {time.time()-t0:.0f}s", flush=True)
json.dump(grids, open(OUT/"occupancy_grids.json", "w"), separators=(",", ":"))
json.dump(cat, open(OUT/"compound_catalogue.json", "w"), separators=(",", ":"))
print("sizes MB:", {f.name: round(f.stat().st_size/1e6, 2) for f in OUT.glob("*.json")})
