from back_end_mip.domain.enums import CollectorType

class ScanValidator:
    def validate_printer(self, printer)-> tuple[bool, str|None]:
            validations = [
                (printer.ip is not None, "IP não informado"),
                (CollectorType(printer.collector_type).requires_collector, "Coleta automatizada não requerida")
            ]
            
            for valid, error in validations:
                if not valid:
                    return (valid, error)
            
            return (True, None)
        
    