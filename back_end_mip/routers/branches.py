#from ..dependencies import get_token_header
from ..models import Branch, BranchNetwork
from ..database import get_session

from fastapi import APIRouter, Depends, HTTPException

from http import HTTPStatus

from typing import Annotated

from sqlalchemy.orm import Session

from ..schemas import(
    BranchPublic,
    ListBranchPublic,
    BranchNetworksPublic
)

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/branches",
    tags=["Branches"],
    #dependencies=[Depends(get_token_header)], Adicionar futuramente quando estiver implementado funcional
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ListBranchPublic
)
def read_branches(
    session:SessionDep
):
    branches = Branch.get_all(session)
    
    if len(branches) == 0:
        raise HTTPException(status_code=404, detail="Table is empty")
    return {"branches": branches}


@router.get(
    "/{branch_id}",
    status_code=HTTPStatus.OK,
    response_model=BranchPublic
)
def read_branch(branch_id:str, session: SessionDep):
    branch = Branch.get_by_id(branch_id, session)
    
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.get(
    "/{branch_id}/networks",
    status_code=HTTPStatus.OK,
    response_model=BranchNetworksPublic
)
def read_branch_networks(branch_id:str, session: SessionDep):
    networks = BranchNetwork.get_by_branch_id(branch_id, session)

    if len(networks) == 0:
        raise HTTPException(
            status_code=404,
            detail="Networks by branch id not found"
        )

    return {
        "branch_id": branch_id,
        "networks": networks
    }

