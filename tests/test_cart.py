def test_cart_caps_quantity_at_stock(client):
    client.post("/cart/add/1", data={"quantity": 99})
    response = client.get("/cart/")
    assert b'value="3"' in response.data
