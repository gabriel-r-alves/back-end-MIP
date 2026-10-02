#from ..dependencies import get_token_header
from ..models import Printer
from ..database import get_session

from fastapi import APIRouter, Depends, HTTPException

from http import HTTPStatus

from typing import Annotated

from sqlalchemy.orm import Session

from ..schemas import(
    Message,
    PrinterPublic,
    ListPrinterPublic
)

SessionDep = Annotated[Session, Depends(get_session)]


router = APIRouter(
    prefix="/printers",
    tags=["Printers"],
    #dependencies=[Depends(get_token_header)], Adicionar futuramente quando estiver implementado funcional
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ListPrinterPublic
)
def read_printers(
    session:SessionDep
):
    printers = Printer.get_all(session)
    if len(printers) == 0:
        raise HTTPException(status_code=404, detail="Table is empty")
    return {"printers": printers}


@router.get(
    "/{printer_serial}",
    status_code=HTTPStatus.OK,
    response_model=PrinterPublic
)
def read_printer(printer_serial: str, session:SessionDep):
    printer = Printer.get_by_serial(printer_serial, session)
    if printer is None:
        raise HTTPException(status_code=404, detail="Printer not found")
    return printer
