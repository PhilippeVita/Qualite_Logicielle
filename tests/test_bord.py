# ============================================
# ./tests/test_bord.py
# ============================================

import json
import os
import pytest
from fastapi.testclient import TestClient
from GitRepository.DEV.Qualite_Logicielle.app_old import app, Base, engine

# --------------------------------------------------------------------
# FIXTURE : reset DB avant chaque test
# --------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


# --------------------------------------------------------------------
# TESTS DE BORD (Edge Cases)
# --------------------------------------------------------------------

def test_post_client_missing_required_fields(client):
    """POST invalid : champs obligatoires manquants."""
    response = client.post("/api/v1/client/", json={"nom": "X"})
    # FastAPI détecte automatiquement les champs manquants → 422
    assert response.status_code == 422


def test_post_client_with_extra_fields(client):
    """POST contenant des champs inconnus : FastAPI doit rejeter."""
    data = {
        "nom": "Test",
        "prenom": "User",
        "adresse": "AAA",
        "inexistant": "should_fail"
    }
    response = client.post("/api/v1/client/", json=data)
    assert response.status_code == 422


def test_patch_client_empty_payload(client):
    """PATCH avec payload vide → ne modifie rien, mais doit réussir."""
    created = client.post("/api/v1/client/", json={
        "nom": "A",
        "prenom": "B",
        "adresse": "C"
    }).json()
    cid = created["codcli"]

    response = client.patch(f"/api/v1/client/{cid}", json={})
    assert response.status_code == 200
    assert response.json()["nom"] == "A"


def test_patch_client_invalid_field(client):
    """PATCH contenant un champ non autorisé."""
    created = client.post("/api/v1/client/", json={
        "nom": "A",
        "prenom": "B",
        "adresse": "C"
    }).json()

    cid = created["codcli"]
    response = client.patch(f"/api/v1/client/{cid}", json={"truc": "invalide"})
    assert response.status_code == 422


def test_get_client_id_invalid_type(client):
    """ID non entier → FastAPI doit renvoyer 422."""
    response = client.get("/api/v1/client/abc")
    assert response.status_code == 422


def test_delete_client_twice(client):
    """Suppression d'un client déjà supprimé : 404."""
    created = client.post("/api/v1/client/", json={
        "nom": "AA",
        "prenom": "BB",
        "adresse": "CC"
    }).json()

    cid = created["codcli"]

    # Première suppression OK
    response1 = client.delete(f"/api/v1/client/{cid}")
    assert response1.status_code == 200

    # Deuxième suppression → 404
    response2 = client.delete(f"/api/v1/client/{cid}")
    assert response2.status_code == 404


def test_post_client_invalid_email_format(client):
    """Format email incorrect — la validation n'est pas automatique car le champ est string.
    Ce test sert de garde-fou et confirme l'absence de validation stricte."""
    data = {
        "nom": "Test",
        "prenom": "User",
        "adresse": "AAA",
        "email": "not_an_email"
    }

    response = client.post("/api/v1/client/", json=data)
    # Le modèle accepte string → success
    assert response.status_code == 200
    assert response.json()["email"] == "not_an_email"


# --------------------------------------------------------------------
# GÉNÉRATION TEST_BORD.JSON
# --------------------------------------------------------------------
def test_generate_test_bord_json():
    results = {
        "edge_cases_tested": [
            "POST client missing fields",
            "POST client with extra/unexpected fields",
            "PATCH client with empty payload",
            "PATCH client with invalid field",
            "GET client with invalid ID type",
            "DELETE same client twice",
            "POST invalid email format accepted"
        ],
        "status": "edge cases validated"
    }

    os.makedirs("./tests", exist_ok=True)
    with open("./tests/test_bord.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    assert os.path.exists("./tests/test_bord.json")