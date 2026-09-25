#!/usr/bin/env python3
"""Download the official RawNet2 checkpoint with parallel HTTP ranges."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import tempfile
import urllib.request
from pathlib import Path


DEFAULT_URL = "https://www.asvspoof.org/asvspoof2021/pre_trained_DF_RawNet2.zip"


def remote_size(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request) as response:
        return int(response.headers["Content-Length"])


def download_part(url: str, start: int, end: int, path: Path) -> None:
    request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(request) as response, path.open("wb") as output:
        if response.status != 206:
            raise RuntimeError(f"Server ignored byte range {start}-{end}: HTTP {response.status}")
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    expected = end - start + 1
    if path.stat().st_size != expected:
        raise RuntimeError(f"Incomplete part {path.name}: expected {expected} bytes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", type=Path, default=Path("pre_trained_DF_RawNet2.zip"))
    parser.add_argument("--workers", type=int, default=24)
    args = parser.parse_args()

    size = remote_size(args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rawnet2-download-") as tmp:
        tmpdir = Path(tmp)
        part_size = (size + args.workers - 1) // args.workers
        jobs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for index, start in enumerate(range(0, size, part_size)):
                end = min(start + part_size - 1, size - 1)
                part = tmpdir / f"part-{index:03d}"
                jobs.append((index, pool.submit(download_part, args.url, start, end, part), part))
            for index, future, _ in jobs:
                future.result()
                print(f"Downloaded part {index + 1}/{len(jobs)}", flush=True)

        temporary_output = args.output.with_suffix(args.output.suffix + ".complete")
        with temporary_output.open("wb") as output:
            for _, _, part in jobs:
                with part.open("rb") as source:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
        if temporary_output.stat().st_size != size:
            raise RuntimeError("Assembled file has the wrong size")
        os.replace(temporary_output, args.output)
    print(f"Saved {args.output} ({size} bytes)")


if __name__ == "__main__":
    main()
