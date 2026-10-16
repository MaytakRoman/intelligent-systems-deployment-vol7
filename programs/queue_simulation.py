from heapq import heapify, heappop, heappush
from math import ceil, isfinite


def quantile_nearest_rank(values, level):
    if not values or not 0 < level <= 1:
        raise ValueError("Нужны значения и уровень от 0 до 1")
    ordered = sorted(values)
    # Ближайший ранг; в NumPy совпадает с method="inverted_cdf".
    return ordered[ceil(level * len(ordered)) - 1]


def simulate(arrivals, service_s, workers, deadline_s):
    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 1:
        raise ValueError("Число исполнителей должно быть целым")
    if not isfinite(service_s) or service_s <= 0:
        raise ValueError("Время обслуживания должно быть положительным")
    if not isfinite(deadline_s) or deadline_s <= 0:
        raise ValueError("Срок должен быть положительным")
    arrivals = sorted(arrivals)
    if not arrivals or any(not isfinite(t) or t < 0 for t in arrivals):
        raise ValueError("Нужны конечные неотрицательные моменты")
    free_at = [0.0] * workers
    heapify(free_at)
    latencies, waits = [], []
    for arrival in arrivals:
        available = heappop(free_at)
        start = max(arrival, available)
        finish = start + service_s
        waits.append(start - arrival)
        latencies.append(finish - arrival)
        heappush(free_at, finish)
    violations = sum(t > deadline_s + 1e-12 for t in latencies)
    return {
        "count": len(latencies),
        "p95_s": quantile_nearest_rank(latencies, 0.95),
        "max_wait_s": max(waits),
        "violations": violations,
    }


if __name__ == "__main__":
    arrivals = [i / 18 for i in range(540)]
    for workers in (1, 2):
        result = simulate(arrivals, 0.07, workers, 0.45)
        print(workers, result)
