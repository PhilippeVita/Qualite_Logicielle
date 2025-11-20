# ./tests/test_exceptions.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from GitRepository.DEV.Qualite_Logicielle.app_old import app, Base, engine, ClientRepository, ClientService

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------
# 1. ClientRepository.delete_client : client None → exception
# ---------------------------------------------------------
def test_repository_delete_none_client():
    repo = ClientRepository(db=None)

    with pytest.raises(Exception):
        repo.delete_client(None)


# ---------------------------------------------------------
# 2. ClientRepository.patch_client : client None
# ---------------------------------------------------------
def test_repository_patch_none_client():
    repo = ClientRepository(db=None)

    with pytest.raises(Exception):
        repo.patch_client(None, {"nom": "Test"})


# ---------------------------------------------------------
# 3. ClientService.delete_client : client inexistant renvoie exception
# ---------------------------------------------------------
def test_service_delete_missing_client():
    service = ClientService(repository=ClientRepository(db=engine))

    with pytest.raises(Exception):
        service.delete_client(9999)


# ---------------------------------------------------------
# 4. DELETE endpoint : exception interne simulée avec monkeypatch
# ---------------------------------------------------------
def test_delete_client_internal_error(monkeypatch):
    def fake_delete(*args, **kwargs):
        raise SQLAlchemyError("DB error")

    monkeypatch.setattr(ClientRepository, "delete_client", fake_delete)

    response = client.delete("/api/v1/client/1")

    assert response.status_code == 500
    assert "internal error" in response.json()["detail"].lower()


# ---------------------------------------------------------
# 5. GET /client/{id} : id non entier (FastAPI validation exception)
# ---------------------------------------------------------
def test_get_client_invalid_id_type():
    response = client.get("/api/v1/client/abc")
    assert response.status_code == 422


# ---------------------------------------------------------
# 6. POST client : erreur Pydantic interne simulée
# ---------------------------------------------------------
def test_create_client_pydantic_internal(monkeypatch):
    from pydantic import ValidationError

    def fake_init(*args, **kwargs):
        raise ValidationError.from_exception_data("ClientPost", [])

    monkeypatch.setattr("app.ClientPost", fake_init)

    response = client.post("/api/v1/client/", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "adresse": "Rue X"
    })

    assert response.status_code == 422


# ---------------------------------------------------------
# 7. DELETE endpoint : id valide mais déclenche None → 404 attendu
# (couverture d’un chemin manquant dans delete_client)
# ---------------------------------------------------------
def test_delete_client_none_path():
    response = client.delete("/api/v1/client/9999")
    assert response.status_code == 404