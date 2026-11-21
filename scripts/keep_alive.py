"""
Backend Keep-Alive Cron / Ping Script for Wax and Warmth
--------------------------------------------------------
Periodically pings the backend API endpoint to prevent free-tier
hosting (such as Render, Railway, Koyeb, Neon DB) from spinning down
or sleeping after inactivity (Render's timeout is 15 minutes).

Zero external dependencies - uses standard library only.

Usage:
    # Run continuously (default: pings every 10 minutes)
    python keep_alive.py

    # Custom URL
    python keep_alive.py --url https://wax-and-warmth.onrender.com/api/health/

    # Custom interval (e.g., every 8 minutes)
    python keep_alive.py --interval 8

    # Run once (for external cron jobs or Windows Task Scheduler)
    python keep_alive.py --once
"""

import argparse
from datetime import datetime, timedelta
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get(
    'BACKEND_PING_URL',
    os.environ.get('BACKEND_URL', 'https://wax-and-warmth.onrender.com/api/settings/')
)
DEFAULT_INTERVAL_MINUTES = 10
DEFAULT_TIMEOUT_SECONDS = 30


def log(level: str, message: str) -> None:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now_str}] [{level}] {message}", flush=True)


def ping(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS, method: str = 'GET') -> bool:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'WaxAndWarmth-KeepAlive/1.0 (+https://wax-and-warmth.shop)',
            'Accept': 'application/json, */*',
        },
        method=method.upper(),
    )

    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            duration_ms = int((time.time() - start_time) * 1000)
            status = response.getcode()
            log('SUCCESS', f"Status {status} OK from {url} ({duration_ms}ms) - Backend is awake!")
            return True
    except urllib.error.HTTPError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        # Even a 401, 404, or 403 means the server process is awake and responded!
        if e.code in (200, 204, 301, 302, 307, 308, 401, 403):
            log('AWAKE', f"Server responded with status {e.code} ({duration_ms}ms) - Backend is awake!")
            return True
        log('WARNING', f"HTTP Error {e.code} ({e.reason}) from {url} after {duration_ms}ms")
        return False
    except urllib.error.URLError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        log('ERROR', f"Connection failed to {url}: {e.reason} ({duration_ms}ms)")
        return False
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        log('ERROR', f"Unexpected error pinging {url}: {e} ({duration_ms}ms)")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Wax and Warmth Backend Keep-Alive Service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--url',
        '-u',
        default=DEFAULT_URL,
        help="URL of the backend endpoint to ping",
    )
    parser.add_argument(
        '--interval',
        '-i',
        type=float,
        default=float(os.environ.get('PING_INTERVAL_MINUTES', DEFAULT_INTERVAL_MINUTES)),
        help="Interval between pings in minutes",
    )
    parser.add_argument(
        '--timeout',
        '-t',
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="HTTP request timeout in seconds",
    )
    parser.add_argument(
        '--method',
        '-m',
        default='GET',
        choices=['GET', 'HEAD'],
        help="HTTP method to use",
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help="Run a single ping and exit (useful for OS cron or Task Scheduler)",
    )

    args = parser.parse_args()

    # Ensure URL is formatted
    target_url = args.url.strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    interval_sec = max(10, int(args.interval * 60))

    print("=" * 65)
    print(" Wax & Warmth Backend Keep-Alive Monitor")
    print(f" Target URL : {target_url}")
    print(f" Method     : {args.method}")
    print(f" Interval   : {args.interval} minutes ({interval_sec} seconds)")
    print(f" Timeout    : {args.timeout} seconds")
    print("=" * 65)

    if args.once:
        success = ping(target_url, timeout=args.timeout, method=args.method)
        sys.exit(0 if success else 1)

    # Continuous loop
    try:
        while True:
            ping(target_url, timeout=args.timeout, method=args.method)
            next_time = (datetime.now() + timedelta(seconds=interval_sec)).strftime('%H:%M:%S')
            log('INFO', f"Next ping scheduled at {next_time} (in {args.interval:g} min). Press Ctrl+C to stop.\n")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\nKeep-alive monitor stopped by user.")
        sys.exit(0)


if __name__ == '__main__':
    main()
