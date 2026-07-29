from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class QRResult:
    """
    Represents the result of generating a QR code.
    """

    filename: str

    path: Path

    command: str