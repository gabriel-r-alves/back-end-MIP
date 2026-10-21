from ..models import Printer
from ..database import get_session

from fastapi import APIRouter, Depends, HTTPException

from http import HTTPStatus

from typing import Annotated

from sqlalchemy.orm import Session

from ..schemas import(
    ScanTargetPublic,
    ListScanTargetPublic
)

SessionDep = Annotated[Session, Depends(get_session)]


router = APIRouter(
    prefix="/targets",
    tags=["Targets"],
    #dependencies=[Depends(get_token_header)], Adicionar futuramente quando estiver implementado funcional
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ListScanTargetPublic
)
def read_targets(
    session:SessionDep
):
    printers = Printer.get_all_scannable(session)
    
    if len(printers) == 0:
        raise HTTPException(status_code=404, detail="Table is empty")
    
    targets_list = [
        ScanTargetPublic(
            ip=printer.ip,
            branch_id=int(printer.branch_current_id),
            network_id=int(printer.network_id) if printer.network_id is not None else None,
            collector_type=printer.collector_type
        ) for printer in printers
    ]
    
    return {"targets": targets_list}


