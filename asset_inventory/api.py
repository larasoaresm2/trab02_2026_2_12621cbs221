"""Read-only HTTP API over the same JSON files the menu writes."""

from flask import Flask, jsonify

from asset_inventory.inventory import Inventory
from asset_inventory.risk import RiskAnalysis
from asset_inventory.storage import JsonStorage


def problem(status, title, detail):
    """Error response in the Problem Details format (RFC 9457)."""
    response = jsonify({"type": "about:blank", "title": title, "status": status, "detail": detail})
    response.status_code = status
    response.content_type = "application/problem+json"
    return response


def create_app(folder="data"):
    """Build the Flask application that reads the inventory from `folder`."""
    app = Flask(__name__)
    storage = JsonStorage(folder)

    def load_inventory():
        # Read the files on every request: the menu may have changed them
        inventory = Inventory()
        storage.load(inventory)
        return inventory

    @app.errorhandler(ValueError)
    def data_unavailable(error):
        return problem(503, "Data unavailable", str(error))

    @app.errorhandler(404)
    def not_found(error):
        return problem(404, "Not Found", "The requested URL does not exist.")

    @app.get("/health")
    def health():
        load_inventory()
        return {"status": "ok"}

    @app.get("/v1/equipments")
    def list_equipments():
        inventory = load_inventory()
        return jsonify([equipment.to_dict() for equipment in inventory.list_equipments()])

    @app.get("/v1/equipments/<int:equipment_id>")
    def get_equipment(equipment_id):
        equipment = load_inventory().get_equipment(equipment_id)
        if equipment is None:
            return problem(404, "Not Found", f"Equipment {equipment_id} not found.")
        return equipment.to_dict()

    @app.get("/v1/vulnerabilities")
    def list_vulnerabilities():
        inventory = load_inventory()
        return jsonify([v.to_dict() for v in inventory.list_vulnerabilities()])

    @app.get("/v1/risk")
    def risk_report():
        inventory = load_inventory()
        try:
            rows = RiskAnalysis(inventory).compute()
        except ValueError as error:
            return problem(422, "Risk cannot be computed", str(error))
        return jsonify(
            [
                {
                    "id": equipment.id,
                    "name": equipment.name,
                    "own_risk": round(float(own), 2),
                    "effective_risk": round(float(effective), 2),
                }
                for equipment, own, effective in rows
            ]
        )

    return app
