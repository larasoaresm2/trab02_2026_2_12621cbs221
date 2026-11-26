from typing import Any


class Equipment:
    """Base class: any IT asset in the inventory."""

    def __init__(
        self,
        equipment_id: int,
        name: str,
        owner: str,
        location: str,
        description: str,
        vulnerability_ids: list[int] | None = None,
    ) -> None:
        self.id = equipment_id
        self.name = name
        self.owner = owner
        self.location = location
        self.description = description

        if vulnerability_ids is None:
            vulnerability_ids = []
        self.vulnerability_ids = vulnerability_ids

    def exposure_factor(self) -> float:
        """How much this type of equipment amplifies its own risk."""
        return 1.0

    def add_vulnerability(self, vulnerability_id: int) -> None:
        if vulnerability_id not in self.vulnerability_ids:
            self.vulnerability_ids.append(vulnerability_id)

    def remove_vulnerability(self, vulnerability_id: int) -> None:
        if vulnerability_id in self.vulnerability_ids:
            self.vulnerability_ids.remove(vulnerability_id)

    def to_dict(self) -> dict[str, Any]:
        """Turn the equipment into a dict that the json module can save."""
        return {
            "type": type(self).__name__,
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "location": self.location,
            "description": self.description,
            "vulnerability_ids": list(self.vulnerability_ids),
        }

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.name} ({type(self).__name__}) | "
            f"owner: {self.owner} | location: {self.location}"
        )


class Server(Equipment):
    def exposure_factor(self) -> float:
        return 1.2


class Notebook(Equipment):
    def exposure_factor(self) -> float:
        return 1.0


class Router(Equipment):
    def exposure_factor(self) -> float:
        return 1.3


class WebApplication(Equipment):
    def exposure_factor(self) -> float:
        return 1.5


class Database(Equipment):
    def exposure_factor(self) -> float:
        return 0.8


# Factory: the "type" saved in the JSON says which class to rebuild
EQUIPMENT_CLASSES: dict[str, type[Equipment]] = {
    "Equipment": Equipment,
    "Server": Server,
    "Notebook": Notebook,
    "Router": Router,
    "WebApplication": WebApplication,
    "Database": Database,
}


def equipment_from_dict(data: dict[str, Any]) -> Equipment:
    """Rebuild an equipment of the right subclass from a dict read from JSON.

    The vulnerability links are restored by JsonStorage through Inventory.link,
    so that they are validated like any other link.
    """
    equipment_class = EQUIPMENT_CLASSES.get(data["type"])
    if equipment_class is None:
        raise ValueError(f"Unknown equipment type: {data['type']}")
    return equipment_class(
        data["id"], data["name"], data["owner"], data["location"], data["description"]
    )
