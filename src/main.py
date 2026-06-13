from __future__ import annotations

from pathlib import Path

from .gui import AnonymizerApp
from .utils import setup_logging


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    setup_logging(project_root)
    app = AnonymizerApp(project_root)
    app.mainloop()


if __name__ == "__main__":
    main()
