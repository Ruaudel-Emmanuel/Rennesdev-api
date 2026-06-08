# tests/api/test_payment_links.py
def test_create_payment_link(client, api_headers):
    payload = {
        "order_id": "order_test_001",
        "product_name": "Audit IA express",
        "amount_cents": 20000,
        "currency": "eur",
        "customer_email": "jean@example.com"
    }

    response = client.post(
        "/api/v1/payment-links",
        json=payload,
        headers=api_headers,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["success"] is True
    assert data["payment_link_id"].startswith("plink_")
    assert data["url"].startswith("https://")
    assert data["message"] == "Lien de paiement créé"