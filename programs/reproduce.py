"""Reproduce the book's educational calculations using only the standard library."""
from pathlib import Path
from decimal import Decimal
import csv
import json
from queue_simulation import simulate
from cost_model import month_cost, cumulative_effect
from reliability import zero_event_upper
from verify_bundle import verify_bundle

def main():
    root = Path(__file__).resolve().parents[1]
    spec = json.loads((root / "data/site_parameters.json").read_text(encoding="utf-8"))
    dest = root / "lab_results"
    dest.mkdir(exist_ok=True)
    def cost(count, timely=None):
        return month_cost(count=str(count), coverage=spec["coverage"],
                          repeat=spec["repeat_share"], timely=timely or spec["timely_share"],
                          unit_manual=spec["unit_manual_rub"], system=spec["monthly_system_rub"])
    arrivals = [i / spec["peak_rate_per_s"] for i in range(spec["peak_rate_per_s"] * spec["peak_duration_s"])]
    queue = {str(n): simulate(arrivals, float(spec["service_s"]), n, float(spec["deadline_s"])) for n in (1, 2)}
    volumes = spec["ramp_volumes"] + [spec["month_count"]] * (spec["months"] - len(spec["ramp_volumes"]))
    total = -Decimal(spec["initial_rub"])
    trajectory = [(0, total)]
    for month, volume in enumerate(volumes, 1):
        total += cost(volume)["effect"]
        trajectory.append((month, total))
    flat = -Decimal(spec["initial_rub"]) + Decimal(spec["months"]) * cost(spec["month_count"])["effect"]
    report = {"educational": True, "month": cost(spec["month_count"]),
              "timely_995": cost(spec["month_count"], "0.995"),
              "stationary_effect_36_months": flat, "ramp_effect_36_months": total,
              "first_positive_month": next(m for m, v in trajectory if v > 0),
              "zero_events_upper_n10000": zero_event_upper(10000), "queue_peak": queue,
              "bundle_integrity": verify_bundle(root / "examples/bundle", root / "examples/bundle/manifest.json"),
              "production_approval": False}
    serial = json.loads(json.dumps(report, default=str))
    (dest / "summary.json").write_text(json.dumps(serial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (dest / "calendar.csv").open("w", newline="", encoding="utf-8") as stream:
        w = csv.writer(stream); w.writerow(["month", "cumulative_effect_rub"]); w.writerows(trajectory)
    expected = json.loads((root / "control_results/summary.json").read_text(encoding="utf-8")) if (root / "control_results/summary.json").exists() else None
    if expected is not None and serial != expected:
        raise SystemExit("Control mismatch; inspect parameters and generated results")
    print(json.dumps(serial, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
