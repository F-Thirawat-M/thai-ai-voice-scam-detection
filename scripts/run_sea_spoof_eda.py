"""Execute SEA-Spoof EDA with this Python, saving restricted outputs locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signal-all", action="store_true", help="Decode every Thai clip instead of a stratified sample")
    parser.add_argument("--no-audio-hashes", action="store_true", help="Skip whole-file SHA-256 checks")
    args = parser.parse_args()

    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from jupyter_client import AsyncKernelManager

    source = ROOT / "data/exploration/sea_spoof/sea_spoof_eda.ipynb"
    output = ROOT / "data/exploration/sea_spoof/outputs"
    output.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    # Change runtime settings in memory only; the source notebook stays clean.
    settings = next(cell for cell in notebook.cells if cell.cell_type == "code")
    if args.signal_all:
        settings.source = settings.source.replace('SIGNAL_SCOPE = "sample"', 'SIGNAL_SCOPE = "all"')
    if args.no_audio_hashes:
        settings.source = settings.source.replace("HASH_AUDIO = True", "HASH_AUDIO = False")

    def cell_started(cell, cell_index):
        if cell.cell_type == "code":
            print(f"Executing cell {cell_index + 1}/{len(notebook.cells)}: {cell.source.splitlines()[0]}", flush=True)

    manager = AsyncKernelManager(kernel_name="python3", ip="127.0.0.1")
    # Never accidentally execute with a system Python or a friend's environment.
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = NotebookClient(notebook, km=manager, timeout=1200,
                            resources={"metadata": {"path": str(ROOT)}},
                            on_cell_start=cell_started)
    executed = client.execute(cleanup_kc=True)
    nbformat.validate(executed)
    destination = output / "sea_spoof_eda.executed.ipynb"
    nbformat.write(executed, destination)
    html, _ = HTMLExporter().from_notebook_node(executed)
    (output / "sea_spoof_eda.html").write_text(html, encoding="utf-8")
    print(f"Executed notebook: {destination}", flush=True)
    print(f"HTML report: {output / 'sea_spoof_eda.html'}", flush=True)
    print("Source notebook, Parquet, manifests and audio were not modified.", flush=True)


if __name__ == "__main__":
    main()
