from back_end_mip.domain.enums import CollectorType
from dataclasses import dataclass


@dataclass
class ScanTarget:
    ip: str
    branch_id: int
    network_id: int | None
    collector_type: CollectorType
    
