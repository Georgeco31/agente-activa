from fastapi.testclient import TestClient


def test_create_customer_from_api(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers",
        json={
            "display_name": "Cliente API",
            "phone": "0987654321",
            "alias": "Cliente del Norte",
            "address": "Calle API # 10",
            "reference": "Porton Verde",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["created"] is True
    assert data["customer"]["normalized_name"] == "cliente api"
    assert data["customer"]["phones"][0]["phone_e164"] == "+593987654321"


def test_get_customer_by_id(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(display_name="Cliente Detalle")

    response = client.get(f"/api/v1/customers/{customer.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(customer.id)
    assert data["display_name"] == "Cliente Detalle"
    assert len(data["phones"]) == 1
    assert len(data["aliases"]) == 1
    assert len(data["addresses"]) == 1


def test_search_customer_by_phone(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(phone="0999627968")

    response = client.get("/api/v1/customers/search", params={"phone": "0999627968"})

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(customer.id)


def test_search_customer_by_alias(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(alias="Dona Maria")

    response = client.get("/api/v1/customers/search", params={"alias": "Do\u00f1a Mar\u00eda"})

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(customer.id)


def test_detect_duplicate_from_api(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(phone="0999627968")

    response = client.post(
        "/api/v1/customers/detect-duplicates",
        json={"phone": "+593999627968"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["customer_id"] == str(customer.id)
    assert "telefono exacto" in data[0]["reasons"]
    assert data[0]["score"] >= 100


def test_add_phone_from_api(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(phone=None)

    response = client.post(
        f"/api/v1/customers/{customer.id}/phones",
        json={"phone": "0991112223", "label": "nuevo"},
    )

    assert response.status_code == 201
    assert response.json()["normalized_phone"] == "+593991112223"


def test_add_alias_from_api(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(alias=None)

    response = client.post(
        f"/api/v1/customers/{customer.id}/aliases",
        json={"alias": "Se\u00f1ora del Port\u00f3n"},
    )

    assert response.status_code == 201
    assert response.json()["normalized_alias"] == "senora del porton"


def test_add_address_from_api(
    client: TestClient, create_test_customer
) -> None:
    customer = create_test_customer(address=None)

    response = client.post(
        f"/api/v1/customers/{customer.id}/addresses",
        json={
            "address": "Av. Quito y Loja",
            "reference": "Frente al parque",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["normalized_address"] == "av quito y loja"
    assert data["normalized_reference"] == "frente al parque"


def test_prevents_duplicate_phone_from_api(
    client: TestClient, create_test_customer
) -> None:
    create_test_customer(display_name="Cliente Existente", phone="0999627968")
    other_customer = create_test_customer(display_name="Otro Cliente", phone=None)

    response = client.post(
        f"/api/v1/customers/{other_customer.id}/phones",
        json={"phone": "+593999627968"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CUSTOMER_PHONE_ALREADY_EXISTS"
    assert response.json()["error"]["message"] == "Phone is already registered."


def test_health_endpoint_still_works(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
