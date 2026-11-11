"""Tests for the read-only API, using Flask's test client (no real server)."""

import pytest

from asset_inventory.api import create_app
from asset_inventory.dependency import Dependency
from asset_inventory.equipment import Router, Server
from asset_inventory.inventory import Inventory
from asset_inventory.storage import JsonStorage
from asset_inventory.vulnerability import Vulnerability


@pytest.fixture
def folder(tmp_path):
    """Save a small inventory in a temporary folder, like the menu would."""
    inventory = Inventory()
    inventory.add_equipment(Server(1, "Web", "Lara", "Lab", "web server"))
    inventory.add_equipment(Router(2, "Edge", "Lara", "Rack", "router"))
    inventory.add_vulnerability(Vulnerability(10, "SQL injection", "Web", 9.8))
    inventory.link(1, 10)
    inventory.add_dependency(Dependency(2, 1, 0.4))
    JsonStorage(tmp_path).save(inventory)
    return tmp_path


@pytest.fixture
def client(folder):
    return create_app(folder).test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_equipments(client):
    response = client.get("/v1/equipments")
    assert response.status_code == 200
    names = [equipment["name"] for equipment in response.get_json()]
    assert names == ["Web", "Edge"]


def test_get_equipment(client):
    response = client.get("/v1/equipments/1")
    assert response.status_code == 200
    assert response.get_json()["vulnerability_ids"] == [10]


def test_unknown_equipment_is_problem_details(client):
    response = client.get("/v1/equipments/99")
    assert response.status_code == 404
    assert response.content_type == "application/problem+json"
    assert response.get_json()["detail"] == "Equipment 99 not found."


def test_unknown_url_is_problem_details(client):
    response = client.get("/v1/nothing")
    assert response.status_code == 404
    assert response.get_json()["title"] == "Not Found"


def test_list_vulnerabilities(client):
    response = client.get("/v1/vulnerabilities")
    assert response.get_json()[0]["cvss"] == 9.8


def test_risk_report(client):
    rows = client.get("/v1/risk").get_json()
    assert [row["name"] for row in rows] == ["Web", "Edge"]
    assert rows[1]["own_risk"] == 0
    assert rows[1]["effective_risk"] == pytest.approx(0.4 * rows[0]["effective_risk"], abs=0.01)


def test_risk_without_equipments(tmp_path):
    client = create_app(tmp_path).test_client()
    response = client.get("/v1/risk")
    assert response.status_code == 422


def test_broken_file_gives_503(folder, client):
    (folder / "equipments.json").write_text("{not json")
    response = client.get("/health")
    assert response.status_code == 503
