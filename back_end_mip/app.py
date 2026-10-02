from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import printers
from .routers import branches
from .routers import branch_networks


app = FastAPI()
app.include_router(printers.router)
app.include_router(branches.router)
app.include_router(branch_networks.router)

# temporariamente futuramente migrar para um midleware separado, atualmente para testes e uso interno
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'message': 'Olá mundo!'}

