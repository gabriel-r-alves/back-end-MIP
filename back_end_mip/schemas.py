from typing import Optional, Dict
from pydantic import BaseModel


class Message(BaseModel):
    message: str


class PrinterPublic(BaseModel):
    num_serial: str
    model: Optional[str]
    branch_current_id: int
    ip: Optional[str]
    status: str
    counter: int
    

class ListPrinterPublic(BaseModel):
    printers: list[PrinterPublic]
    
    
class BranchPublic(BaseModel):
    id: int | str
    name: str
    

class ListBranchPublic(BaseModel):
    branches: list[BranchPublic]
    

class BranchNetworkPublic(BaseModel):
    id: int
    ip_version: str
    start_readable: str
    end_readable: str
    description: str


class BranchNetworksPublic(BaseModel):
    branch_id: int
    networks: list[BranchNetworkPublic]


class ListBranchesNetworksPublic(BaseModel):
    networks_by_branch_id: list[BranchNetworksPublic]
    
    