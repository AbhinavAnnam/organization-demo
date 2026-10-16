"""In-memory organization creation and listing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Organization:
    """A named organization."""

    name: str


class OrganizationDirectory:
    """Store organizations in memory and return them in creation order."""

    def __init__(self) -> None:
        self._organizations: list[Organization] = []

    def create_organization(self, name: str) -> Organization:
        """Create and store an organization with the supplied name."""
        organization = Organization(name=name)
        self._organizations.append(organization)
        return organization

    def list_organizations(self) -> list[Organization]:
        """Return a snapshot of organizations in creation order."""
        return list(self._organizations)
