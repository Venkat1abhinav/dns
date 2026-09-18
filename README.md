# DNS Benchmark

A small Python tool for benchmarking the response latency of public DNS resolvers.

It tests multiple DNS providers against a collection of commonly used websites, collects latency statistics, and produces both CSV data and a visual comparison.

## What it does

The benchmark currently tests:

| Provider   | DNS Server       |
| ---------- | ---------------- |
| Cloudflare | `1.1.1.1`        |
| Google     | `8.8.8.8`        |
| Quad9      | `9.9.9.9`        |
| AdGuard    | `94.140.14.14`   |
| OpenDNS    | `208.67.222.222` |

Each resolver is tested against 10 domains with 20 queries per domain.

That produces:

```text
5 DNS servers × 10 domains × 20 iterations
= 1000 DNS queries
```

The benchmark measures:

* Average latency
* Median latency
* Minimum latency
* Maximum latency
* Number of successful samples

Results are also broken down per domain.

## Example domains

The benchmark currently includes:

```text
google.com
github.com
youtube.com
wikipedia.org
cloudflare.com
amazon.com
reddit.com
stackoverflow.com
python.org
mozilla.org
```

## How it works

```text
                  DNS Benchmark
                       │
          ┌────────────┼────────────┐
          │            │            │
      Cloudflare     Google       Quad9
          │            │            │
          └────────────┼────────────┘
                       │
                    dig A
                       │
                 DNS Resolver
                       │
                 Query latency
                       │
              ┌────────┴────────┐
              │                 │
         Statistics          Raw data
              │                 │
              ▼                 ▼
       Console results       CSV files
              │
              ▼
       Matplotlib chart
```

DNS providers are benchmarked concurrently using Python's `ThreadPoolExecutor`.

Each DNS query is executed through the system `dig` command and the query time reported by `dig` is collected.

## Requirements

* Python `3.14+`
* [`dig`](https://man.archlinux.org/man/dig.1)
* [`uv`](https://docs.astral.sh/uv/)
* Internet connection

Python dependencies are managed through the project's `pyproject.toml`.

## Installation

Clone the repository:

```bash
git clone https://github.com/Venkat1abhinav/dns.git
cd dns
```

Install dependencies with `uv`:

```bash
uv sync
```

## Running

Run the benchmark with:

```bash
uv run dns
```

The benchmark will:

1. Test all configured DNS providers.
2. Query every configured domain 20 times.
3. Calculate latency statistics.
4. Print overall results.
5. Print per-domain results.
6. Generate CSV files.
7. Generate a benchmark chart.

## Output

The benchmark generates three files:

```text
dns_results.csv
dns_site_results.csv
dns_benchmark.png
```

### `dns_results.csv`

Contains overall statistics for each DNS provider:

```text
provider
server
average_ms
median_ms
minimum_ms
maximum_ms
samples
```

### `dns_site_results.csv`

Contains statistics for every provider/domain combination:

```text
provider
server
domain
average_ms
median_ms
minimum_ms
maximum_ms
samples
```

### `dns_benchmark.png`

A visual comparison of the average DNS query latency for each provider.

## Configuration

The DNS servers, domains, number of iterations, and timeout are defined in the source:

```python
DNS_SERVERS = {
    "Cloudflare": "1.1.1.1",
    "Google": "8.8.8.8",
    "Quad9": "9.9.9.9",
    "AdGuard": "94.140.14.14",
    "OpenDNS": "208.67.222.222",
}

ITERATIONS = 20
TIMEOUT = 3
```

You can add or remove DNS providers and domains directly from these configuration values.

## Important

DNS performance is highly dependent on the network and location from which the benchmark is run.

A resolver that is faster on one network may not be faster on another.

The results from this project should therefore be treated as **measurements of the environment where the benchmark was executed**, not as universal rankings of DNS providers.

## Project Structure

```text
dns/
├── src/
│   └── dns/
│       └── __init__.py
│
├── dns_benchmark.png
├── dns_results.csv
├── dns_site_results.csv
├── pyproject.toml
├── uv.lock
└── README.md
```

## Tech Stack

* Python
* `dig`
* `concurrent.futures`
* Matplotlib
* CSV
* uv

## Why I built this

This project is a small experiment in measuring DNS resolver performance rather than relying on assumptions about which DNS provider is "fastest."

It also explores:

* DNS resolution
* subprocess execution
* network latency measurement
* concurrent workloads
* statistical aggregation
* CSV data generation
* data visualization

## License

No license has been specified yet.
