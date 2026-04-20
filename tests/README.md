# Inugami Load Testing

This directory contains a simple Python harness for sending multiple concurrent HTTP requests to an Inugami server and measuring how it behaves under light traffic.

The goal is not to replace a full benchmarking tool, but to give you an easy, portable way to sanity-check:

- concurrent request handling
- endpoint responsiveness
- basic throughput
- status-code stability
- latency behavior across multiple routes

## Included file

- `inugami_load_test.py` - standard-library-only concurrent HTTP load tester for Inugami endpoints

## Requirements

- Python 3
- a running Inugami server

No third-party Python packages are required.

## Start your Inugami app first

For example:

```bash
hachi main.hachi -go
````

Or run your already-built server binary.

By default, the test harness assumes your server is listening on:

```text
http://127.0.0.1:8080
```

## Basic usage

Run a mixed GET test against a few common endpoints:

```bash
python3 inugami_load_test.py --base-url http://127.0.0.1:8080 \
  --endpoint / --endpoint /health --endpoint /version \
  --requests 200 --concurrency 20
```

## Test with POST routes too

If your app exposes POST endpoints such as `/submit` or `/save`, include them like this:

```bash
python3 inugami_load_test.py --base-url http://127.0.0.1:8080 \
  --endpoint GET:/ --endpoint GET:/health --endpoint POST:/submit --endpoint POST:/save \
  --requests 400 --concurrency 40
```

## Save the results as JSON

You can write a machine-readable summary to disk:

```bash
python3 inugami_load_test.py --base-url http://127.0.0.1:8080 \
  --endpoint / --endpoint /health --endpoint /version \
  --requests 300 --concurrency 30 --json-out load_results.json
```

## Command-line options

### `--base-url`

Base server URL to test.

Default:

```text
http://127.0.0.1:8080
```

Example:

```bash
--base-url http://127.0.0.1:8080
```

---

### `--endpoint`

Endpoint to include in the traffic mix.

Repeat this flag multiple times.

Supported forms:

- `/path`
- `GET:/path`
- `POST:/path`

Examples:

```bash
--endpoint /
--endpoint /health
--endpoint GET:/version
--endpoint POST:/submit
```

If no endpoints are provided, the harness defaults to:

- `/`
- `/health`
- `/version`

---

### `--requests`

Total number of requests to send across all workers.

Example:

```bash
--requests 200
```

---

### `--concurrency`

Number of concurrent worker threads.

Example:

```bash
--concurrency 20
```

---

### `--timeout`

Per-request timeout in seconds.

Example:

```bash
--timeout 5
```

---

### `--seed`

Random seed used to choose the endpoint mix.

Useful when you want repeatable runs.

Example:

```bash
--seed 1337
```

---

### `--json-out`

Optional output file path for a JSON summary.

Example:

```bash
--json-out load_results.json
```

## What the harness reports

At the end of a run, the tool prints:

- total requests
- successful requests
- errors
- wall-clock duration
- throughput in requests per second
- total bytes received
- latency minimum
- latency mean
- latency median
- latency p95
- latency p99
- latency max
- status-code counts
- per-endpoint latency summary
- error breakdown if any failures occurred

## Example output

```text
=== Inugami Load Test Summary ===
Total requests:     200
Successful:         200
Errors:             0
Wall clock:         1.842 s
Throughput:         108.58 req/s
Bytes received:     5420

Latency min:        1.11 ms
Latency mean:       7.94 ms
Latency median:     5.62 ms
Latency p95:        18.40 ms
Latency p99:        31.72 ms
Latency max:        44.08 ms
```

## Suggested first tests

### Smoke test

A small sanity run to confirm the server is healthy:

```bash
python3 inugami_load_test.py --requests 50 --concurrency 5
```

### Light mixed traffic

A basic concurrent check for multiple routes:

```bash
python3 inugami_load_test.py --base-url http://127.0.0.1:8080 \
  --endpoint / --endpoint /health --endpoint /version --endpoint /landing \
  --requests 200 --concurrency 20
```

### GET + POST mix

Useful if you want to exercise both route types:

```bash
python3 inugami_load_test.py --base-url http://127.0.0.1:8080 \
  --endpoint GET:/ --endpoint GET:/health --endpoint POST:/submit --endpoint POST:/save \
  --requests 500 --concurrency 50
```

## Notes

- This is a simple harness, not a full synthetic benchmarking suite.
- It is good for quick concurrent sanity checks and development-stage performance snapshots.
- For very high-volume or protocol-level benchmarking, you may later want a dedicated load-testing tool.
- POST requests currently send a small default JSON payload, but the current Inugami demo routes do not depend on the request body.

## Good workflow

A practical workflow looks like this:

1. start the Inugami server
2. run a small smoke test
3. run a larger concurrent mix
4. inspect p95/p99 latency and any errors
5. save a JSON summary if you want to compare runs later

This makes it easy to spot regressions as Inugami grows.
