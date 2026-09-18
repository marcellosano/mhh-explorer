"""Per-cell single-hazard summaries from the Phase-2 daily masks (MPI only for the mockup):
extreme days per year, mean exceedance on extreme days, and the threshold map, per variable x window."""
import xarray as xr, numpy as np, json, sys, pathlib, time
V = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
VARS = ["tasmax", "hurs_low", "soilmoist_dry", "pr_deficit", "pr", "qtot", "soilmoist_wet", "ps", "sfcwind", "hurs_high"]
WIN = {"hist": ("historical", ["1981_1990", "1991_2000", "2001_2010"])}
for s in ["ssp126", "ssp370", "ssp585"]:
    WIN[f"{s}_mid"] = (s, ["2031_2040", "2041_2050", "2051_2060"]); WIN[f"{s}_late"] = (s, ["2071_2080", "2081_2090", "2091_2100"])
res = {"windows": list(WIN), "vars": VARS, "days": {}, "exceed": {}, "threshold": {}, "season": {}}
t0 = time.time()
for v in VARS:
    th = xr.open_dataarray(V/"Phase2_Thresholds"/f"threshold_{v}_historical.nc")
    res["threshold"][v] = [None if not np.isfinite(x) else float(f"{x:.6g}") for x in th.values.flatten()]
    if "lat" not in res: res["lat"] = th.lat.values.tolist(); res["lon"] = th.lon.values.tolist()
    for key, (scen, decs) in WIN.items():
        days = np.zeros(th.shape); exs = np.zeros(th.shape); seas = np.zeros((4,) + th.shape); ndays = 0
        for dec in decs:
            m = xr.open_dataarray(V/"Phase2_Extremes"/f"extremes_{v}_{scen}_{dec}.nc")
            e = xr.open_dataarray(V/"Phase2_Extremes"/f"exceedance_{v}_{scen}_{dec}.nc")
            m = m.transpose("time", "lat", "lon"); e = e.transpose("time", "lat", "lon"); mv = m.values.astype(bool); days += mv.sum(0); exs += np.abs(e.values).sum(0); ndays += mv.shape[0]
            mon = m.time.dt.month.values; q = (mon % 12) // 3  # 0=DJF 1=MAM 2=JJA 3=SON
            for k in range(4): seas[k] += mv[q == k].sum(0)
        yrs = ndays / 365.25
        res["days"][f"{v}|{key}"] = np.round(days / yrs, 2).flatten().tolist()
        res["exceed"][f"{v}|{key}"] = [float(f"{x:.4g}") for x in np.where(days > 0, exs / np.maximum(days, 1), 0).flatten()]
        res["season"][f"{v}|{key}"] = [np.round(seas[k] / yrs, 2).flatten().tolist() for k in range(4)]
    print(v, f"{time.time()-t0:.0f}s", flush=True)
json.dump(res, open(OUT/"single_hazard_mpi.json", "w"), separators=(",", ":"))
print("size MB", round((OUT/"single_hazard_mpi.json").stat().st_size/1e6, 2))
