from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("twd")
except PackageNotFoundError as e:
    __version__ = "unknown"
