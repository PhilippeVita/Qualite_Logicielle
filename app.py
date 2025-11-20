"""Application FastAPI pour la gestion des clients avec validation, persistance et documentation."""

from typing import Optional, List

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session


# Configuration de la base de données
CONNECTION_STRING = "sqlite:///./test.db"

engine = create_engine(
    CONNECTION_STRING,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Client(Base):
    """Modèle SQLAlchemy représentant un client."""

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


class ClientBase(BaseModel):
    """Schéma Pydantic de base pour un client."""

    nom: str
    prenom: str
    genre: Optional[str] = None
    adresse: str
    complement_adresse: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    newsletter: Optional[int] = 0


class ClientPost(ClientBase):
    """Schéma pour la création d’un client."""
    pass


class ClientPatch(BaseModel):
    """Schéma pour la mise à jour partielle d’un client."""

    nom: Optional[str] = None
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    complement_adresse: Optional[str] = None
    genre: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    newsletter: Optional[int] = None


class ClientInDB(ClientBase):
    """Schéma enrichi avec l’identifiant du client."""

    codcli: int

    class Config:
        """Configuration pour l’utilisation avec ORM."""
        orm_mode = True


class ClientRepository:
    """Couche d’accès aux données client."""

    def __init__(self, db: Session):
        """Initialise le repository avec une session SQLAlchemy."""
        self.db = db

    def get_all_clients(self):
        """Retourne tous les clients."""
        return self.db.query(Client).all()

    def get_client_by_id(self, client_id: int):
        """Retourne un client par son identifiant."""
        return self.db.query(Client).get(client_id)

    def create_client(self, data: dict):
        """Crée un nouveau client."""
        client = Client(**data)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def patch_client(self, client_id: int, updates: dict):
        """
        Met à jour partiellement un client existant.

        Seuls les champs valides du modèle sont modifiés.
        Retourne None si le client n’existe pas.
        """
        client = self.get_client_by_id(client_id)
        if not client:
            return None

        for field, value in updates.items():
            if hasattr(client, field):
                setattr(client, field, value)

        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, client_id: int):
        """Supprime un client existant."""
        client = self.get_client_by_id(client_id)
        if not client:
            return None
        self.db.delete(client)
        self.db.commit()
        return client


class ClientService:
    """Couche métier pour la gestion des clients."""

    def __init__(self, repository: ClientRepository):
        """Initialise le service avec un repository."""
        self.repository = repository

    def get_all_clients(self):
        """Retourne tous les clients."""
        return self.repository.get_all_clients()

    def get_client_by_id(self, client_id: int):
        """Retourne un client par son identifiant."""
        return self.repository.get_client_by_id(client_id)

    def create_client(self, new_client: ClientPost):
        """Crée un client à partir d’un schéma Pydantic."""
        data = new_client.dict()
        return self.repository.create_client(data)

    def patch_client(self, client_id: int, client_patch: ClientPatch):
        """Met à jour partiellement un client."""
        data = client_patch.dict(exclude_unset=True)
        return self.repository.patch_client(client_id, data)

    def delete_client(self, client_id: int):
        """Supprime un client existant."""
        client = self.repository.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        self.repository.delete_client(client_id)


app = FastAPI()

router = APIRouter(
    prefix="/api/v1/client",
    tags=["client"]
)


def get_db():
    """Fournit une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_client_repository(db: Session = Depends(get_db)):
    """Injecte le repository client."""
    return ClientRepository(db)


def get_client_service(repo: ClientRepository = Depends(get_client_repository)):
    """Injecte le service client."""
    return ClientService(repo)


@router.get("/", response_model=List[ClientInDB])
def get_clients(service: ClientService = Depends(get_client_service)):
    """Retourne tous les clients."""
    return service.get_all_clients()


@router.get("/{client_id}", response_model=ClientInDB)
def get_client(client_id: int, service: ClientService = Depends(get_client_service)):
    """Retourne un client par son identifiant."""
    client = service.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client


@router.post("/", response_model=ClientInDB)
def create_client(client: ClientPost, service: ClientService = Depends(get_client_service)):
    """Crée un nouveau client."""
    return service.create_client(client)


@router.patch("/{client_id}", response_model=ClientInDB)
def patch_client(
    client_id: int,
    client: ClientPatch,
    service: ClientService = Depends(get_client_service)
):
    """Met à jour partiellement un client."""
    patched_client = service.patch_client(client_id, client)
    if not patched_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return patched_client


@router.delete("/{client_id}")
def delete_client(client_id: int, service: ClientService = Depends(get_client_service)):
    """Supprime un client existant."""
    service.delete_client(client_id)
    return {"message": "Client supprimé"}


app.include_router(router)


@app.get("/")
def root():
    """Point d’entrée de l’API."""
    return {"message": "FastAPI opérationnel"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )
