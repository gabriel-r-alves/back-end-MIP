import asyncio
import ipaddress

from back_end_mip.database.models import Printer, BranchNetwork

from back_end_mip.loggin import log_error, log_info

from . import ScanValidator, PostScan
from . import  PrinterScanTargetResp, NetworkScanTargetResp

from back_end_mip.domain.dtos import ScanData, PrinterData, ScanTarget
from domain.enums import CollectorType, ConnectionStatus, ScanStatus
    

class Scanner:
    def __init__(self, printer_repository = None, branch_repository = None, branch_network_repository = None, error_repository= None) -> None:
            self.printer_repository = printer_repository
            self.branch_repository = branch_repository
            self.network_repository = branch_network_repository
            self.error_repository = error_repository
    
            self.validator = ScanValidator()
            self.post_scan = PostScan()
    
            self.MAX_IPS_PER_NETWORK = 4096
    
    
    def targets_scan_printers(self) -> PrinterScanTargetResp:
        prep_scan_targerts = PrinterScanTargetResp(scan_targets=[], invalid_printers=[])
        
        log_info("Verificando repositório de impressoras...")
        if self.printer_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return prep_scan_targerts
        log_info("SUCESSO!")

        log_info("Verificando repositório de erros...")
        if self.error_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return prep_scan_targerts
        log_info("SUCESSO!")

        printers_db = self.printer_repository.get_all_printers()
        
        log_info("Obtendo impressoras do Banco de Dados...")
        if not printers_db:
            log_error("[X] Sem impressoras cadastrada no Banco de Dados.")
            return prep_scan_targerts
        
        for printer in printers_db:
            log_info("Iniciando validação da impressora...")
            valid, error = self.validator.validate_printer(printer)
            
            if not valid:
                log_error(f"[X] Impressora invalida! motivo: {error}")
                scan_resp = ScanData(
                    ip=printer.ip,
                    network_id=printer.network_id,
                    branch_id=printer.branch_current_id,
                    connection=ConnectionStatus.INITIALIZED,
                    status=ScanStatus.INVALID_PRINTER,
                    collector_type=None,
                    printer_data=self._printer_to_data(printer)
                )
                
                prep_scan_targerts.invalid_printers.append(scan_resp)
    
            log_info("Impressora válida!")
            # Não sobrescrever o objeto original — converte localmente
            collector_type = CollectorType(printer.collector_type)
            target = ScanTarget(
                ip=printer.ip,
                branch_id=printer.branch_current_id,
                network_id=printer.network_id,
                collector_type=collector_type
            )
            
            prep_scan_targerts.scan_targets.append(target)
            
        
        log_info(f"Impressoras válida para scan sendo enviadas: {len(prep_scan_targerts.scan_targets)}")
        log_info(f"Impressoras inválida para scan ignoradas: {len(prep_scan_targerts.invalid_printers)}")

        return prep_scan_targerts


    def targets_scan_networks(self) -> NetworkScanTargetResp:
        prep_scan_targets = NetworkScanTargetResp(scan_targets=[])
        
        log_info("Verificando repositório de Filiais...")
        if self.branch_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return prep_scan_targets
        log_info("SUCESSO!")

        log_info("Verificando repositório de Redes das filais...")
        if self.network_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return prep_scan_targets
        log_info("SUCESSO!")

        log_info("Obtendo filiais do db...")
        branches_db = self.branch_repository.get_all_branches()

        if not branches_db:
            log_error("[X] Lista vazia! Nenhuma filial cadastrada.")
            return prep_scan_targets

        targets_scan_branches = []

        for branch in branches_db:
            log_info(f"Obtendo redes da filial {branch.id} {branch.name}")

            networks = self.network_repository.get_by_filial(branch.id)
            if not networks:
                log_error("[X] Não possui rede cadastrada!")
                continue

            for network in networks:
                if not network.active:
                    continue
            
                ips_to_scan = self.__scan_network(network)
                
                for ip in ips_to_scan:
                    
        return targets_scan_branches


    def __scan_network(self, network: BranchNetwork) -> list[str]:
        try:
            # Converte os endereços legíveis de volta para objetos de IP
            start_addr = ipaddress.ip_address(network.start_readable)
            end_addr = ipaddress.ip_address(network.end_readable)

            if start_addr.version != end_addr.version:
                log_error(
                    f"[X] Rede {network.id}: IPs de versões diferentes: "
                    f"{start_addr} -> {end_addr}"
                )
                return []

            total_ips = int(end_addr) - int(start_addr) + 1

            if total_ips <= 0:
                log_error(
                    f"[X] Rede {network.id}: range inválido: "
                    f"{start_addr} -> {end_addr}"
                )
                return []

            if total_ips > self.MAX_IPS_PER_NETWORK:
                log_error(
                    f"[X] Rede {network.id}: range muito grande: "
                    f"{start_addr} -> {end_addr} "
                    f"({total_ips} IPs)"
                )
                return []

            log_info(
                f"[SCAN] Rede {network.id} - {network.description}: "
                f"{start_addr} -> {end_addr} "
                f"({total_ips} IPs)"
            )
            
            ips_to_scan = [
                str(ipaddress.ip_address(ip_int))
                for ip_int in range(int(start_addr), int(end_addr) + 1)
            ]

            log_info(f"Lista de {len(ips_to_scan)} IPs criada.")

            
        except Exception as e:
            log_error(
                f"Erro ao processar range da rede {network.id}: {e}"
            )
            return []

        log_info(
            f"Finalizada rede {network.id}."
        )

        return ips_to_scan


    async def _network_ping_and_scan(self, network: BranchNetwork, ip: str) -> ScanData:
        """Pipeline por rede de filial — prepara metadata e chama pipeline genérico."""
        return await self._ping_and_scan(
            ip=ip,
            branch_id=network.branch_id,
            network_id=network.id,
            collector_type=network.collector_type
        )


    # mover para validator antes de sync
    def _generate_scan_error(self, printer, error):
        error = ErrorCounter(
            num_serial=printer.num_serial,
            branch_id=printer.branch_current_id,
            ip=printer.ip,
            status=printer.status,
            named_error=error
        )
        return error


    def _printer_to_data(self, printer:Printer):
        return PrinterData(
            num_serial=printer.num_serial,
            model=printer.model,
            counter=str(printer.counter)
        )