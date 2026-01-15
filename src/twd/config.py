

from pathlib import Path
from pydantic import BaseModel, Field, validator
import json
import os
import sys

def get_config_path() -> Path:
    """Cross-platform config location"""

    if sys.platform == "win32":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

    config_dir = base / "twd"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir / "config.json"

def get_data_path() -> Path:
    """Cross-platform data location"""

    if sys.platform == "win32":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / "twd"
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir / "data.csv"

class Config(BaseModel):
    """App configuration"""

    data_path: Path = Field(default_factory=get_data_path)
    
    @validator("data_path")
    def validate_path(cls, v):
        """Expand home and ensure path exists"""

        path = Path(v).expanduser()
        if not path.exists():
            path = get_data_path()
        return path

    @classmethod
    def load(cls) -> "Config":
        """Load config from file, create with defaults"""
        config_file = get_config_path()

        if not config_file.exists():
            config = cls()
            config.save()
            return config

        try:
            with open(config_file, "rb") as f:
                data = json.load(f)

            return cls(**data)
        except Exception as e:
            print(f"Warning: config file corrupted, using defaults: {e}")
            return cls()

    def save(self) -> None:
        """save config to file"""

        config_file = get_config_path()
        
        data = self.model_dump(mode="json")

        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
