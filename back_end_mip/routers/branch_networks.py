#from ..dependencies import get_token_header
from ..models import BranchNetwork
from ..database import get_session

from fastapi import APIRouter, Depends, HTTPException

from http import HTTPStatus

from typing import Annotated

from sqlalchemy.orm import Session

from ..schemas import(
    BranchNetworkPublic,
    BranchNetworksPublic,
    ListBranchesNetworksPublic
)

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/networks",
    tags=["Networks"],
    #dependencies=[Depends(get_token_header)], Adicionar futuramente quando estiver implementado funcional
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ListBranchesNetworksPublic
)
def read_networks(
    session:SessionDep
):
    networks = BranchNetwork.get_all(session)
    
    if len(networks) == 0:
        raise HTTPException(status_code=404, detail="Table is empty")
    
    networks_by_branch = {}
    
    for network in networks:
        if network.branch_id not in networks_by_branch:
            networks_by_branch[network.branch_id] = []

        networks_by_branch[network.branch_id].append(
            BranchNetworkPublic(
                id=network.id,
                ip_version=network.ip_version,
                start_readable=network.start_readable,
                end_readable=network.end_readable,
                description=network.description
            )
        )
        
    return {
        "networks_by_branch_id": [
            {
                "branch_id": branch_id,
                "networks": networks
            }
            for branch_id, networks in networks_by_branch.items()
        ]
    }


@router.get(
    "/{network_id}",
    status_code=HTTPStatus.OK,
    response_model=BranchNetworkPublic
)
def read_network_by_id(network_id:str, session: SessionDep):
    network = BranchNetwork.get_by_id(network_id, session)
    
    if network is None:
        raise HTTPException(status_code=404, detail="Network by id not found")
    return network

