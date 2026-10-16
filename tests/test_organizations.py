from organization_demo import Organization, OrganizationDirectory


def test_create_organization_returns_and_stores_organization() -> None:
    directory = OrganizationDirectory()

    organization = directory.create_organization("Northwind")

    assert organization == Organization(name="Northwind")
    assert directory.list_organizations() == [organization]


def test_list_organizations_preserves_creation_order() -> None:
    directory = OrganizationDirectory()
    directory.create_organization("Northwind")
    directory.create_organization("Contoso")

    organizations = directory.list_organizations()

    assert [organization.name for organization in organizations] == [
        "Northwind",
        "Contoso",
    ]


def test_list_organizations_returns_a_snapshot() -> None:
    directory = OrganizationDirectory()
    directory.create_organization("Northwind")

    organizations = directory.list_organizations()
    organizations.clear()

    assert [organization.name for organization in directory.list_organizations()] == [
        "Northwind"
    ]
