from dataclasses import dataclass

from .printer_data import PrinterData
from back_end_mip.domain.enums import ScanErrorType

@dataclass
class ScanResp:
    success: bool
    printer_data: PrinterData | None
    error: str | None
    error_type: ScanErrorType | None = None