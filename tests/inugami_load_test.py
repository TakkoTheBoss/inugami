#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import random
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    body: bytes = b""
    headers: tuple[tuple[str, str], ...] = ()

    @property
    def label(self) -> str:
        return f"{self.method} {self.path}"


@dataclass
class Result:
    endpoint: str
    ok: bool
    status: int | None
    elapsed_ms: float
    error: str | None = None
    bytes_received: int = 0


def parse_endpoint(raw: str) -> Endpoint:
    if ":" in raw and raw.split(":", 1)[0].upper() in {"GET", "POST"}:
        method, path = raw.split(":", 1)
        method = method.upper().strip()
        path = path.strip()
    else:
        method = "GET"
        path = raw.strip()

    if not path.startswith("/"):
        raise ValueError(f"Endpoint path must start with '/': {raw}")

    if method == "POST":
        body = b'{"demo":true}'
        headers = (("Content-Type", "application/json"),)
    else:
        body = b""
        headers = ()

    return Endpoint(method=method, path=path, body=body, headers=headers)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    index = (len(ordered) - 1) * pct
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def perform_request(base_url: str, endpoint: Endpoint, timeout: float) -> Result:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", endpoint.path.lstrip("/"))
    req = urllib.request.Request(url=url, data=endpoint.body or None, method=endpoint.method)
    for k, v in endpoint.headers:
        req.add_header(k, v)

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            status = getattr(resp, "status", None)
            ok = status is not None and 200 <= status < 400
            return Result(
                endpoint=endpoint.label,
                ok=ok,
                status=status,
                elapsed_ms=elapsed_ms,
                bytes_received=len(body),
            )
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        try:
            body = e.read()
            byte_count = len(body)
        except Exception:
            byte_count = 0
        return Result(
            endpoint=endpoint.label,
            ok=False,
            status=e.code,
            elapsed_ms=elapsed_ms,
            error=f"HTTPError {e.code}",
            bytes_received=byte_count,
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return Result(
            endpoint=endpoint.label,
            ok=False,
            status=None,
            elapsed_ms=elapsed_ms,
            error=type(e).__name__ + (f": {e}" if str(e) else ""),
            bytes_received=0,
        )


def run_test(
    base_url: str,
    endpoints: list[Endpoint],
    total_requests: int,
    concurrency: int,
    timeout: float,
    seed: int,
) -> list[Result]:
    rng = random.Random(seed)
    results: list[Result] = []
    results_lock = threading.Lock()

    planned = [rng.choice(endpoints) for _ in range(total_requests)]

    def worker(ep: Endpoint) -> None:
        result = perform_request(base_url, ep, timeout)
        with results_lock:
            results.append(result)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(worker, planned))

    return results


def summarize(results: list[Result]) -> dict:
    elapsed_values = [r.elapsed_ms for r in results]
    ok_count = sum(1 for r in results if r.ok)
    err_count = len(results) - ok_count
    status_counts = Counter(r.status for r in results)
    endpoint_latencies: dict[str, list[float]] = defaultdict(list)
    error_counts = Counter(r.error for r in results if r.error)
    total_bytes = sum(r.bytes_received for r in results)

    for r in results:
        endpoint_latencies[r.endpoint].append(r.elapsed_ms)

    return {
        "total": len(results),
        "ok": ok_count,
        "errors": err_count,
        "bytes_received": total_bytes,
        "min_ms": min(elapsed_values) if elapsed_values else 0.0,
        "mean_ms": statistics.fmean(elapsed_values) if elapsed_values else 0.0,
        "median_ms": statistics.median(elapsed_values) if elapsed_values else 0.0,
        "p95_ms": percentile(elapsed_values, 0.95),
        "p99_ms": percentile(elapsed_values, 0.99),
        "max_ms": max(elapsed_values) if elapsed_values else 0.0,
        "status_counts": dict(sorted(status_counts.items(), key=lambda kv: (kv[0] is None, kv[0]))),
        "endpoint_latencies": {
            k: {
                "count": len(v),
                "mean_ms": statistics.fmean(v),
                "median_ms": statistics.median(v),
                "p95_ms": percentile(v, 0.95),
                "max_ms": max(v),
            }
            for k, v in sorted(endpoint_latencies.items())
        },
        "error_counts": dict(error_counts),
    }


def print_summary(summary: dict, wall_clock_s: float) -> None:
    total = summary["total"]
    rps = total / wall_clock_s if wall_clock_s > 0 else 0.0

    print("\n=== Inugami Load Test Summary ===")
    print(f"Total requests:     {total}")
    print(f"Successful:         {summary['ok']}")
    print(f"Errors:             {summary['errors']}")
    print(f"Wall clock:         {wall_clock_s:.3f} s")
    print(f"Throughput:         {rps:.2f} req/s")
    print(f"Bytes received:     {summary['bytes_received']}")
    print()
    print(f"Latency min:        {summary['min_ms']:.2f} ms")
    print(f"Latency mean:       {summary['mean_ms']:.2f} ms")
    print(f"Latency median:     {summary['median_ms']:.2f} ms")
    print(f"Latency p95:        {summary['p95_ms']:.2f} ms")
    print(f"Latency p99:        {summary['p99_ms']:.2f} ms")
    print(f"Latency max:        {summary['max_ms']:.2f} ms")

    print("\nStatus counts:")
    for status, count in summary["status_counts"].items():
        print(f"  {status}: {count}")

    print("\nPer-endpoint:")
    for endpoint, data in summary["endpoint_latencies"].items():
        print(
            f"  {endpoint:<20} "
            f"count={data['count']:<5} "
            f"mean={data['mean_ms']:.2f} ms  "
            f"p95={data['p95_ms']:.2f} ms  "
            f"max={data['max_ms']:.2f} ms"
        )

    if summary["error_counts"]:
        print("\nError breakdown:")
        for err, count in summary["error_counts"].items():
            print(f"  {err}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple concurrent load tester for Inugami.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="Base server URL.")
    parser.add_argument(
        "--endpoint",
        action="append",
        dest="endpoints",
        help="Endpoint to test. Repeat this flag. Forms: /path, GET:/path, POST:/path",
    )
    parser.add_argument("--requests", type=int, default=200, help="Total number of requests.")
    parser.add_argument("--concurrency", type=int, default=20, help="Concurrent worker count.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout in seconds.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for endpoint mix.")
    parser.add_argument("--json-out", default="", help="Optional file path to write JSON summary.")
    args = parser.parse_args()

    raw_endpoints = args.endpoints or ["/", "/health", "/version"]
    try:
        endpoints = [parse_endpoint(e) for e in raw_endpoints]
    except ValueError as e:
        print(f"Argument error: {e}", file=sys.stderr)
        return 2

    if args.requests <= 0:
        print("--requests must be > 0", file=sys.stderr)
        return 2
    if args.concurrency <= 0:
        print("--concurrency must be > 0", file=sys.stderr)
        return 2

    print("Starting Inugami load test...")
    print(f"Base URL:      {args.base_url}")
    print(f"Endpoints:     {', '.join(ep.label for ep in endpoints)}")
    print(f"Requests:      {args.requests}")
    print(f"Concurrency:   {args.concurrency}")
    print(f"Timeout:       {args.timeout:.2f} s")

    t0 = time.perf_counter()
    results = run_test(
        base_url=args.base_url,
        endpoints=endpoints,
        total_requests=args.requests,
        concurrency=args.concurrency,
        timeout=args.timeout,
        seed=args.seed,
    )
    wall_clock_s = time.perf_counter() - t0

    summary = summarize(results)
    print_summary(summary, wall_clock_s)

    if args.json_out:
        payload = {
            "base_url": args.base_url,
            "endpoints": [ep.label for ep in endpoints],
            "requests": args.requests,
            "concurrency": args.concurrency,
            "timeout": args.timeout,
            "wall_clock_s": wall_clock_s,
            "summary": summary,
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"\nWrote JSON summary to: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
