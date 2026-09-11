#!/usr/bin/env python3

import csv
import statistics
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import matplotlib.pyplot as plt


DNS_SERVERS = {
    "Cloudflare": "1.1.1.1",
    "Google": "8.8.8.8",
    "Quad9": "9.9.9.9",
    "AdGuard": "94.140.14.14",
    "OpenDNS": "208.67.222.222",
}

DOMAINS = [
    "google.com",
    "github.com",
    "youtube.com",
    "wikipedia.org",
    "cloudflare.com",
    "amazon.com",
    "reddit.com",
    "stackoverflow.com",
    "python.org",
    "mozilla.org",
]

ITERATIONS = 20
TIMEOUT = 3


def dns_query(server: str, domain: str):
    """Query a DNS server and return latency in milliseconds."""

    try:
        result = subprocess.run(
            [
                "dig",
                f"@{server}",
                domain,
                "A",
                "+stats",
                "+time=2",
                "+tries=1",
            ],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            if "Query time:" in line:
                return float(line.split()[3])

        return None

    except (subprocess.TimeoutExpired, OSError):
        return None


def benchmark_dns(name: str, server: str):
    """Benchmark one DNS server against all domains."""

    print(f"Testing {name} ({server})...")

    all_results = []
    site_results = {}

    for domain in DOMAINS:
        measurements = []

        for _ in range(ITERATIONS):
            latency = dns_query(server, domain)

            if latency is not None:
                measurements.append(latency)
                all_results.append(latency)

        if measurements:
            site_results[domain] = {
                "average": statistics.mean(measurements),
                "median": statistics.median(measurements),
                "minimum": min(measurements),
                "maximum": max(measurements),
                "samples": len(measurements),
            }
        else:
            site_results[domain] = {
                "average": None,
                "median": None,
                "minimum": None,
                "maximum": None,
                "samples": 0,
            }

    if not all_results:
        return {
            "name": name,
            "server": server,
            "average": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "samples": 0,
            "sites": site_results,
        }

    return {
        "name": name,
        "server": server,
        "average": statistics.mean(all_results),
        "median": statistics.median(all_results),
        "minimum": min(all_results),
        "maximum": max(all_results),
        "samples": len(all_results),
        "sites": site_results,
    }


def print_overall_results(results):
    """Print overall DNS results."""

    print()
    print("OVERALL RESULTS")
    print("=" * 90)

    print(
        f"{'Provider':<15}"
        f"{'Server':<18}"
        f"{'Average':>12}"
        f"{'Median':>12}"
        f"{'Min':>12}"
        f"{'Max':>12}"
        f"{'Samples':>10}"
    )

    print("-" * 90)

    for result in results:
        print(
            f"{result['name']:<15}"
            f"{result['server']:<18}"
            f"{result['average']:>9.2f} ms"
            f"{result['median']:>9.2f} ms"
            f"{result['minimum']:>9.2f} ms"
            f"{result['maximum']:>9.2f} ms"
            f"{result['samples']:>10}"
        )


def print_site_results(results):
    """Print per-site benchmark results."""

    print()
    print("PER-SITE RESULTS")
    print("=" * 100)

    for result in results:
        print()
        print(f"{result['name']} ({result['server']})")
        print("-" * 100)

        print(
            f"{'Domain':<25}"
            f"{'Average':>12}"
            f"{'Median':>12}"
            f"{'Min':>12}"
            f"{'Max':>12}"
            f"{'Samples':>10}"
        )

        for domain, stats in result["sites"].items():

            if stats["samples"] == 0:
                print(f"{domain:<25}FAILED")
                continue

            print(
                f"{domain:<25}"
                f"{stats['average']:>9.2f} ms"
                f"{stats['median']:>9.2f} ms"
                f"{stats['minimum']:>9.2f} ms"
                f"{stats['maximum']:>9.2f} ms"
                f"{stats['samples']:>10}"
            )


def save_csv(results):
    """Save overall results to CSV."""

    with open("dns_results.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "provider",
                "server",
                "average_ms",
                "median_ms",
                "minimum_ms",
                "maximum_ms",
                "samples",
            ]
        )

        for result in results:
            writer.writerow(
                [
                    result["name"],
                    result["server"],
                    result["average"],
                    result["median"],
                    result["minimum"],
                    result["maximum"],
                    result["samples"],
                ]
            )


def save_site_csv(results):
    """Save individual site results to CSV."""

    with open("dns_site_results.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "provider",
                "server",
                "domain",
                "average_ms",
                "median_ms",
                "minimum_ms",
                "maximum_ms",
                "samples",
            ]
        )

        for result in results:

            for domain, stats in result["sites"].items():

                writer.writerow(
                    [
                        result["name"],
                        result["server"],
                        domain,
                        stats["average"],
                        stats["median"],
                        stats["minimum"],
                        stats["maximum"],
                        stats["samples"],
                    ]
                )


def create_chart(results):
    """Create DNS performance chart."""

    names = [result["name"] for result in results]
    averages = [result["average"] for result in results]

    plt.figure(figsize=(11, 6))

    bars = plt.bar(names, averages)

    plt.title(
        f"DNS Benchmark "
        f"({len(DOMAINS)} sites × {ITERATIONS} iterations)"
    )

    plt.xlabel("DNS Provider")
    plt.ylabel("Average DNS Query Time (ms)")

    for bar, value in zip(bars, averages):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f} ms",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()

    plt.savefig(
        "dns_benchmark.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.show()


def main():

    total_queries = (
        len(DNS_SERVERS)
        * len(DOMAINS)
        * ITERATIONS
    )

    print("DNS Benchmark")
    print("=" * 60)

    print(f"DNS servers : {len(DNS_SERVERS)}")
    print(f"Sites       : {len(DOMAINS)}")
    print(f"Iterations  : {ITERATIONS}")
    print(f"Total tests : {total_queries}")

    print()

    results = []

    # Test DNS providers concurrently.
    with ThreadPoolExecutor(
        max_workers=len(DNS_SERVERS)
    ) as executor:

        futures = {
            executor.submit(
                benchmark_dns,
                name,
                server,
            ): name
            for name, server in DNS_SERVERS.items()
        }

        for future in as_completed(futures):
            results.append(future.result())

    # Remove failed DNS servers.
    results = [
        result
        for result in results
        if result["average"] is not None
    ]

    # Fastest first.
    results.sort(
        key=lambda result: result["average"]
    )

    print_overall_results(results)

    print_site_results(results)

    save_csv(results)
    save_site_csv(results)

    create_chart(results)

    print()
    print("Files created:")
    print("  dns_results.csv")
    print("  dns_site_results.csv")
    print("  dns_benchmark.png")


if __name__ == "__main__":
    main()