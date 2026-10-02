"""Run the separate remote metadata-only SEA-Spoof notebook, no audio."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from jupyter_client import AsyncKernelManager

    class ProgressClient(NotebookClient):
        def process_message(self, msg, cell, cell_index):
            if msg["msg_type"] == "stream":
                content = msg["content"].get("text", "")
                if any(label in content for label in ("Remote metadata:", "Reading ", "Using verified NEW")):
                    print(content, end="", flush=True)
            return super().process_message(msg, cell, cell_index)

    folder = ROOT / "data/exploration/sea_spoof"
    output = folder / "outputs/metadata_only"
    output.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(folder / "sea_spoof_metadata_eda.ipynb", as_version=4)
    nbformat.validate(notebook)

    def started(cell, cell_index):
        if cell.cell_type == "code":
            print(f"Cell {cell_index + 1}/{len(notebook.cells)}: {cell.source.splitlines()[0]}", flush=True)

    manager = AsyncKernelManager(kernel_name="python3", ip="127.0.0.1")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = ProgressClient(notebook, km=manager, timeout=2400,
                            resources={"metadata": {"path": str(ROOT)}}, on_cell_start=started)
    try:
        notebook = client.execute(cleanup_kc=True)
    except Exception:
        nbformat.write(notebook, output / "sea_spoof_metadata_eda.failed.ipynb")
        raise
    nbformat.validate(notebook)
    nbformat.write(notebook, output / "sea_spoof_metadata_eda.executed.ipynb")
    html, _ = HTMLExporter().from_notebook_node(notebook)
    (output / "sea_spoof_metadata_eda.html").write_text(html, encoding="utf-8")
    print(f"Report: {output / 'sea_spoof_metadata_eda.html'}", flush=True)
    print("No original local dataset files used; no audio column selected.", flush=True)


if __name__ == "__main__":
    main()
