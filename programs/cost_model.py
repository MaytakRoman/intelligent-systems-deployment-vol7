from decimal import Decimal
# Строковые аргументы сохраняют точность при создании Decimal.
def month_cost(
    count="2000000", coverage="0.85",
    repeat="0.04", timely="0.999",
    unit_manual="0.75", system="810000"
):
    n, c, r, a, u, fixed = map(
        Decimal,
        (count, coverage, repeat, timely,
         unit_manual, system)
    )
    values = (n, c, r, a, u, fixed)
    if not all(x.is_finite() for x in values):
        raise ValueError("non-finite input")
    if min(n, u, fixed) < 0:
        raise ValueError("negative input")
    if not all(0 <= x <= 1 for x in (c, r, a)):
        raise ValueError("share outside interval")
    auto = n * c * (1 - r) * a
    manual = n - auto
    baseline = n * u
    process = fixed + manual * u
    return {
        "auto_on_time": auto,
        "manual": manual,
        "baseline": baseline,
        "system": fixed,
        "process": process,
        "effect": baseline - process,
    }

from decimal import Decimal

# Строковые аргументы сохраняют точность при создании Decimal.
def cumulative_effect(volumes, initial="3600000"):
    total = -Decimal(initial)
    rows = [(0, total)]
    for month, volume in enumerate(volumes, 1):
        total += month_cost(count=str(volume))["effect"]
        rows.append((month, total))
    return rows

if __name__ == "__main__":
    volumes = [600000, 1200000, 1600000]
    volumes += [2000000] * 33
    trajectory = cumulative_effect(volumes)
