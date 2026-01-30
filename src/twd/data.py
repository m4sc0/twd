import csv

from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

from .config import Config

class Entry(BaseModel):
    """Data class for a signle TWD Entry"""
    
    alias: str = Field(..., min_length=2, max_length=64)
    path: Path
    name: str = Field(..., min_length=3)
    created_at: datetime = Field(default_factory=datetime.now)

    def __eq__(self, other) -> bool:
        """Compare entries based on their values"""
        if not isinstance(other, Entry):
            return NotImplemented

        return (
                self.alias == other.alias
                and self.path == other.path
                and self.name == other.name
                )

    @validator("alias")
    def validate_alias(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Alias must be alphanumeric with - or _")

        return v.lower()

    @validator("path")
    def validate_path(cls, v):
        path = Path(v).expanduser().resolve()

        return path

    def to_csv(self) -> List[str]:
        """Convert to csv row"""
        return [
                self.alias,
                str(self.path),
                self.name,
                self.created_at.isoformat()
                ]

    @classmethod
    def from_csv(cls, row: List[str]) -> "Entry":
        """create from csv row"""
        return cls(
                alias=row[0],
                path=Path(row[1]),
                name=row[2],
                created_at=datetime.fromisoformat(row[3])
                )

    @classmethod
    def from_values(cls, alias, path, name, created_at) -> "Entry":
        """create from values"""
        return cls(
                alias=alias,
                path=path,
                name=name,
                created_at=created_at
                )

class TwdManager:
    """twd entry manager stored in csv"""

    CSV_HEADERS = ["alias", "path", "name", "created_at"]
    CSV_HEADERS_FANCY = ["Alias", "Path", "Description", "Created at"]

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._ensure_csv_exists()
        self.cwd = str(Path.cwd())

    def _ensure_csv_exists(self) -> None:
        """create csv headers"""
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True) 

            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADERS)

    def _read_all(self) -> List[Entry]:
        """read all entries"""
        entries = []

        with open(self.csv_path, 'r', newline='') as f:
            reader = csv.reader(f)

            next(reader) # skip headers

            for row in reader:
                entries.append(Entry.from_csv(row))

        return entries

    def _write_all(self, entries: List[Entry]) -> None:
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.CSV_HEADERS)

            for entry in entries:
                writer.writerow(entry.to_csv())

    def add(self, alias: str, path: Path, name: Optional[str] = None) -> Entry:
        """Add new entry"""
        entries = self._read_all()

        if any(e.alias == alias.lower() for e in entries):
            raise ValueError(f"Alias '{alias}' already exists")

        if name is None:
            name = Path(path).name

        entry = Entry(alias=alias, path=path, name=name)
        entries.append(entry)
        self._write_all(entries)

        return entry

    def get(self, alias: str) -> Optional[Entry]:
        """get entry by alias"""
        entries = self._read_all()

        for entry in entries:
            if entry.alias == alias.lower():
                return entry

        return None

    def update(self, alias: str, entry: Entry) -> bool:
        """update TWD by alias"""
        if not self.exists(alias):
            return False

        # simplest form of update is remove and add
        self.remove(alias)

        self.add(entry.alias, entry.path, entry.name)

    def remove(self, alias: str) -> None:
        """remove entry by alias"""
        entries = self._read_all()
        original_len = len(entries)

        entries = [e for e in entries if e.alias != alias.lower()]

        if len(entries) == original_len:
            raise KeyError(f"Alias '{alias}' not found")

        self._write_all(entries)

    def list_all(self) -> List[Entry]:
        entries = self._read_all()

        return sorted(entries, key=lambda e: e.created_at)

    def exists(self, alias: str) -> bool:
        return self.get(alias) is not None
