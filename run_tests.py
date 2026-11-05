#!/usr/bin/env python3
"""
E2E Test Runner for Natural Gas Price Modeling & Forecasting Pipeline.

Executes the 4-tier testing hierarchy (60 tests total):
- Tier 1: Feature Coverage (25 tests)
- Tier 2: Boundary & Corner Cases (25 tests)
- Tier 3: Cross-Feature Interactions (5 tests)
- Tier 4: Real-World Workload Scenarios (5 tests)

Usage:
    python run_tests.py             # Run all 60 tests across all tiers
    python run_tests.py --tier 1    # Run Tier 1 only
    python run_tests.py --tier 2    # Run Tier 2 only
    python run_tests.py --tier 3    # Run Tier 3 only
    python run_tests.py --tier 4    # Run Tier 4 only
    python run_tests.py -v          # Verbose output
"""

import argparse
import io
import os
import sys
import time
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TIER_MODULES = {
    1: ("Tier 1: Feature Coverage", "tests.test_tier1"),
    2: ("Tier 2: Boundary & Corner Cases", "tests.test_tier2"),
    3: ("Tier 3: Cross-Feature Interactions", "tests.test_tier3"),
    4: ("Tier 4: Real-World Workload Scenarios", "tests.test_tier4"),
}


def run_tier(tier_num, verbose=False):
    """Run tests for a single tier and return (test_count, passed, failed, errors, duration)."""
    title, mod_name = TIER_MODULES[tier_num]
    loader = unittest.TestLoader()

    try:
        suite = loader.loadTestsFromName(mod_name)
    except Exception as e:
        print(f"Error loading module {mod_name}: {e}")
        return 0, 0, 0, 1, 0.0

    print(f"\n{'='*70}")
    print(f"Executing {title} ({mod_name})")
    print(f"{'='*70}")

    stream = sys.stdout if verbose else io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2 if verbose else 1,
        failfast=False,
    )

    t_start = time.time()
    result = runner.run(suite)
    duration = time.time() - t_start

    if not verbose:
        # If not verbose, print summary dots and any failures/errors
        output = stream.getvalue()
        if output:
            print(output.strip())

    total = result.testsRun
    failed = len(result.failures)
    errors = len(result.errors)
    passed = total - failed - errors

    return total, passed, failed, errors, duration


def main():
    parser = argparse.ArgumentParser(description="Run E2E Test Suite for Natural Gas Modeling Pipeline.")
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run a specific tier (1, 2, 3, or 4). If omitted, runs all tiers.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed verbose output for each test.",
    )
    args = parser.parse_args()

    selected_tiers = [args.tier] if args.tier else [1, 2, 3, 4]

    print(f"{'#'*70}")
    print("NATURAL GAS PRICE MODELING & FORECASTING IN INDIA")
    print("E2E Acceptance & Robustness Test Runner")
    print(f"Workspace Root: {PROJECT_ROOT}")
    print(f"{'#'*70}")

    grand_total = 0
    grand_passed = 0
    grand_failed = 0
    grand_errors = 0
    tier_summaries = []

    start_all = time.time()

    for t in selected_tiers:
        total, passed, failed, errors, duration = run_tier(t, verbose=args.verbose)
        grand_total += total
        grand_passed += passed
        grand_failed += failed
        grand_errors += errors
        tier_title = TIER_MODULES[t][0].split(":")[0]
        tier_summaries.append((tier_title, total, passed, failed, errors, duration))

    total_time = time.time() - start_all

    print(f"\n\n{'='*70}")
    print("TEST SUITE EXECUTION SUMMARY")
    print(f"{'='*70}")
    print(f"{'Tier':<12} | {'Total':<6} | {'Passed':<7} | {'Failed':<7} | {'Errors':<7} | {'Time (s)':<8}")
    print(f"{'-'*12}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*8}")

    for name, tot, p, f, e, dur in tier_summaries:
        status = "OK" if (f == 0 and e == 0) else "FAIL"
        print(f"{name:<12} | {tot:<6} | {p:<7} | {f:<7} | {e:<7} | {dur:<8.2f}")

    print(f"{'-'*12}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*8}")
    print(f"{'TOTAL':<12} | {grand_total:<6} | {grand_passed:<7} | {grand_failed:<7} | {grand_errors:<7} | {total_time:<8.2f}")
    print(f"{'='*70}")

    if grand_failed == 0 and grand_errors == 0:
        print("\nOVERALL STATUS: ALL TESTS PASSED [SUCCESS]")
        sys.exit(0)
    else:
        print(f"\nOVERALL STATUS: {grand_failed} FAILED, {grand_errors} ERRORS [FAILURE]")
        sys.exit(1)


if __name__ == "__main__":
    main()
