# app.py
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Optional, List
from pydantic import BaseModel
import os

# DB config
CONNECTION_STRING = f"sqlite:///./test.db"
engine = create_engine(CONNECTION_STRING, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Client(Base):
    __tablename__ = "t_client"
    codcli = Column(Integer, primary_key=True, index=True)
    nom = Column(String(40), index=True)
    prenom = Column(String(30))
    genre = Column(String(8), default=None)
    adresse = Column(String(50))
    complement_adresse = Column(String(50), default=None)
    tel = Column(String(10), default=None)
    email = Column(String(255), default=None)
    newsletter = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class ClientBase(BaseModel):
    nom: str
    prenom: str
    genre: Optional[str] = None
    adresse: str
    complement_adresse: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    newsletter: Optional[int] = 0

class ClientPost(ClientBase):
    pass

class ClientPatch(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    complement_adresse: Optional[str] = None
    genre: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    newsletter: Optional[int] = None

class ClientInDB(ClientBase):
    codcli: int
    class Config:
        orm_mode = True

# Repository
class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_clients(self):
        return self.db.query(Client).all()

    def get_client_by_id(self, id: int):
        return self.db.query(Client).get(id)

    def create_client(self, data: dict):
        client = Client(**data)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def patch_client(self, id: int, data: dict):
        client = self.get_client_by_id(id)
        if not client:
            return None
        for k, v in data.items():
            setattr(client, k, v)
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, id: int):
        client = self.get_client_by_id(id)
        if not client:
            return None
        self.db.delete(client)
        self.db.commit()
        return client

# Service
class ClientService:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def get_all_clients(self):
        return self.repository.get_all_clients()

    def get_client_by_id(self, client_id: int):
        return self.repository.get_client_by_id(client_id)

    def create_client(self, new_client: ClientPost):
        data = new_client.dict()
        return self.repository.create_client(data)

    def patch_client(self, client_id: int, client_patch: ClientPatch):
        data = client_patch.dict(exclude_unset=True)
        return self.repository.patch_client(client_id, data)

    def delete_client(self, client_id: int):
        client = self.repository.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        self.repository.delete_client(client_id)

# FastAPI app et dépendances
app = FastAPI()
router = APIRouter(prefix="/api/v1/client", tags=["client"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_client_repository(db: Session = Depends(get_db)):
    return ClientRepository(db)

def get_client_service(repo: ClientRepository = Depends(get_client_repository)):
    return ClientService(repo)

# Routes
@router.get("/", response_model=List[ClientInDB])
def get_clients(service: ClientService = Depends(get_client_service)):
    return service.get_all_clients()

@router.get("/{client_id}", response_model=ClientInDB)
def get_client(client_id: int, service: ClientService = Depends(get_client_service)):
    client = service.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client

@router.post("/", response_model=ClientInDB)
def create_client(client: ClientPost, service: ClientService = Depends(get_client_service)):
    return service.create_client(client)

@router.patch("/{client_id}", response_model=ClientInDB)
def patch_client(client_id: int, client: ClientPatch, service: ClientService = Depends(get_client_service)):
    patched_client = service.patch_client(client_id, client)
    if not patched_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return patched_client

@router.delete("/{client_id}")
def delete_client(client_id: int, service: ClientService = Depends(get_client_service)):
    service.delete_client(client_id)
    return {"message": "Client deleted"}

app.include_router(router)

@app.get("/")
def root():
    return {"message": "FastAPI operational"}

# Run si lancé en script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)