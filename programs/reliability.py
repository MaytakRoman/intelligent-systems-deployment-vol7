"""Exact one-sided binomial upper bound for zero violations (formula 3.4)."""
from math import expm1, log

def zero_event_upper(n, alpha=0.05):
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    return -expm1(log(alpha) / n)
