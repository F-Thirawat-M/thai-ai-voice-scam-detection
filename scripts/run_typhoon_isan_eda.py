"""Execute Typhoon metadata-only EDA using this Python; never fetch audio."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from jupyter_client import AsyncKernelManager

    folder = ROOT / "data/exploration/typhoon_thai_dialect_isan"
    source = folder / "typhoon_isan_eda.ipynb"
    output = folder / "outputs"
    output.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)

    def cell_started(cell, cell_index):
        if cell.cell_type == "code":
            print(f"Executing cell {cell_index + 1}/{len(notebook.cells)}: {cell.source.splitlines()[0]}", flush=True)

    manager = AsyncKernelManager(kernel_name="python3", ip="127.0.0.1")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = NotebookClient(notebook, km=manager, timeout=1200,
                            resources={"metadata": {"path": str(ROOT)}},
                            on_cell_start=cell_started)
    executed = client.execute(cleanup_kc=True)
    nbformat.validate(executed)
    destination = output / "typhoon_isan_eda.executed.ipynb"
    nbformat.write(executed, destination)
    html, _ = HTMLExporter().from_notebook_node(executed)
    (output / "typhoon_isan_eda.html").write_text(html, encoding="utf-8")
    print(f"Executed notebook: {destination}", flush=True)
    print(f"HTML report: {output / 'typhoon_isan_eda.html'}", flush=True)
    print("No audio read, downloaded, saved or decoded.", flush=True)


if __name__ == "__main__":
    main()
