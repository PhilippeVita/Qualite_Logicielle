# ============================================
# ./tests/test_erreurs.py
# ============================================

import pytest
from fastapi.testclient import TestClient
from GitRepository.DEV.Qualite_Logicielle.app_old import app, SessionLocal, Base, engine, Client

client = TestClient(app)

# Réinitialisation complète de la DB avant chaque test
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------
# 1. GET /api/v1/client/{id} : client inexistant
# ---------------------------------------------------------
def test_get_client_inexistant():
    response = client.get("/api/v1/client/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Client non trouvé"


# ---------------------------------------------------------
# 2. PATCH /api/v1/client/{id} : client inexistant
# ---------------------------------------------------------
def test_patch_client_inexistant():
    response = client.patch("/api/v1/client/9999", json={"nom": "Test"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Client non trouvé"


# ---------------------------------------------------------
# 3. DELETE /api/v1/client/{id} : client inexistant
# ---------------------------------------------------------
def test_delete_client_inexistant():
    response = client.delete("/api/v1/client/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Client non trouvé"


# ---------------------------------------------------------
# 4. POST /api/v1/client/ : données invalides
# ---------------------------------------------------------
def test_create_client_invalid_missing_fields():
    # Données vides = erreur Pydantic
    response = client.post("/api/v1/client/", json={})
    assert response.status_code == 422  # Unprocessable Entity


# ---------------------------------------------------------
# 5. POST client : champ type incorrect
# ---------------------------------------------------------
def test_create_client_invalid_type():
    response = client.post("/api/v1/client/", json={
        "nom": 123,                 # incorrect type
        "prenom": True,             # incorrect type
        "adresse": ["adresse"]      # incorrect type
    })
    assert response.status_code == 422


# ---------------------------------------------------------
# 6. PATCH : corps vide
# ---------------------------------------------------------
def test_patch_client_empty_body():
    # Créer un client valide
    response = client.post("/api/v1/client/", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "adresse": "123 rue X"
    })
    cid = response.json()["codcli"]

    # PATCH sans données => OK, ne modifie rien mais valide
    response_patch = client.patch(f"/api/v1/client/{cid}", json={})
    assert response_patch.status_code == 200


# ---------------------------------------------------------
# 7. GET /api/v1/client/ : liste vide + test repo/service
# ---------------------------------------------------------
def test_get_clients_empty():
    response = client.get("/api/v1/client/")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------
# 8. root() non testé selon coverage
# ---------------------------------------------------------
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI operational"}
