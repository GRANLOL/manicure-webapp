from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    source = project_root / "bookings.db"
    backup_dir = project_root / "backups"
    backup_dir.mkdir(exist_ok=True)

    if not source.exists():
        print("bookings.db not found")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = backup_dir / f"bookings_{timestamp}.db"
    shutil.copy2(source, destination)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
