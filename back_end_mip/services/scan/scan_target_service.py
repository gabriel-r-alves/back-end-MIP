from dataclasses import dataclass

from back_end_mip.loggin import log_error, log_info
from back_end_mip.domain.dtos import ScanData, ScanTarget

from .scanner import Scanner

@dataclass
class PrinterScanTargetResp:
    scan_targets: list[ScanTarget]
    invalid_printers: list[ScanData]


class ScanTargetService:
    def __init__(self, printer_repository = None, branch_repository = None, branch_network_repository = None, error_repository= None) -> None:
        self.printer_repository = printer_repository
        self.branch_repository = branch_repository
        self.network_repository = branch_network_repository
        self.error_repository = error_repository
        
        self.scanner = Scanner(
            printer_repository=printer_repository,
            branch_repository=branch_repository,
            branch_network_repository=branch_network_repository,
            error_repository=error_repository
        )
    
    
    def collect_scan_data(self, type_scan:str) -> list[ScanTarget]:
        scan_data_list = []
        if type_scan == "db": # temporario
            printer_scan_targets = self.scanner.targets_scan_printers()
            scan_data_list = printer_scan_targets.scan_targets
        
        elif type_scan == "branch": # temporario
            scan_data_list = self.scanner.targets_scan_networks()
        
        # filtrered_scan_data = self._filter_scan_data(scan_data_list)
        return scan_data_list