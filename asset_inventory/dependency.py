from typing import Any


class Dependency:
    """The dependent equipment inherits a fraction of the source equipment's risk.

    In the risk model this is one entry of matrix A:
    A[dependent][source] = fraction.
    """

    def __init__(self, dependent_id: int, source_id: int, fraction: float) -> None:
        if dependent_id == source_id:
            raise ValueError("An equipment cannot depend on itself.")
        if not 0.0 < fraction < 1.0:
            raise ValueError("Fraction must be greater than 0 and less than 1.")
        self.dependent_id = dependent_id
        self.source_id = source_id
        self.fraction = fraction

    def to_dict(self) -> dict[str, Any]:
        """Turn the dependency into a dict that the json module can save."""
        return {
            "dependent_id": self.dependent_id,
            "source_id": self.source_id,
            "fraction": self.fraction,
        }

    def __str__(self) -> str:
        return (
            f"Equipment {self.dependent_id} inherits {self.fraction:.0%} "
            f"of the risk of equipment {self.source_id}"
        )


def dependency_from_dict(data: dict[str, Any]) -> Dependency:
    """Rebuild a dependency from a dict read from JSON (the constructor validates it)."""
    return Dependency(data["dependent_id"], data["source_id"], data["fraction"])
