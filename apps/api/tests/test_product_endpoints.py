from fastapi.testclient import TestClient


def _create_product(
    client: TestClient,
    *,
    sku: str = "BOT20",
    name: str = "Botellon 20 Litros",
    description: str | None = "Agua purificada",
    unit: str = "botellon",
    price: str = "9.50",
    is_active: bool = True,
) -> dict:
    response = client.post(
        "/api/v1/products",
        json={
            "sku": sku,
            "name": name,
            "description": description,
            "unit": unit,
            "price": price,
            "is_active": is_active,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_product_from_api(client: TestClient) -> None:
    data = _create_product(client)

    assert data["sku"] == "BOT20"
    assert data["name"] == "Botellon 20 Litros"
    assert data["unit"] == "botellon"
    assert data["is_active"] is True


def test_create_product_saves_normalized_name(client: TestClient) -> None:
    data = _create_product(client, sku="AGUA600", name="Agua Purificada 600ml")

    assert data["normalized_name"] == "agua purificada 600ml"


def test_create_product_rejects_negative_price(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "NEGATIVO",
            "name": "Producto Invalido",
            "unit": "unidad",
            "price": "-1.00",
        },
    )

    assert response.status_code == 422


def test_create_product_rejects_duplicate_sku(client: TestClient) -> None:
    _create_product(client, sku="SKU-UNICO")

    response = client.post(
        "/api/v1/products",
        json={
            "sku": "SKU-UNICO",
            "name": "Otro Producto",
            "unit": "unidad",
            "price": "5.00",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Product SKU is already registered."


def test_list_products(client: TestClient) -> None:
    product = _create_product(client, sku="LISTA-1")

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert product["id"] in [item["id"] for item in response.json()]


def test_list_products_can_filter_active_products(client: TestClient) -> None:
    active = _create_product(client, sku="ACTIVO", name="Producto Activo")
    inactive = _create_product(
        client,
        sku="INACTIVO",
        name="Producto Inactivo",
        is_active=False,
    )

    response = client.get("/api/v1/products", params={"active_only": "true"})

    assert response.status_code == 200
    product_ids = [item["id"] for item in response.json()]
    assert active["id"] in product_ids
    assert inactive["id"] not in product_ids


def test_get_product_by_id(client: TestClient) -> None:
    product = _create_product(client, sku="DETALLE")

    response = client.get(f"/api/v1/products/{product['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == product["id"]


def test_search_product_by_name(client: TestClient) -> None:
    product = _create_product(client, sku="BUSCAR-NOMBRE", name="Botellon Premium")

    response = client.get(
        "/api/v1/products/search",
        params={"name": "  BOTELLON   PREMIUM "},
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == product["id"]


def test_search_product_by_sku(client: TestClient) -> None:
    product = _create_product(client, sku="BUSCAR-SKU")

    response = client.get("/api/v1/products/search", params={"sku": "BUSCAR-SKU"})

    assert response.status_code == 200
    assert response.json()[0]["id"] == product["id"]


def test_update_product(client: TestClient) -> None:
    product = _create_product(client, sku="ACTUALIZAR")

    response = client.patch(
        f"/api/v1/products/{product['id']}",
        json={"name": "Botellon Actualizado", "price": "11.25"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Botellon Actualizado"
    assert data["normalized_name"] == "botellon actualizado"
    assert data["price"] == "11.25"


def test_deactivate_product(client: TestClient) -> None:
    product = _create_product(client, sku="DESACTIVAR")

    response = client.patch(f"/api/v1/products/{product['id']}/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_health_endpoint_still_works(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
