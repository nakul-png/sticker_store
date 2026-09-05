def test_checkout_creates_pending_order_without_gateway(client):
    client.post("/cart/add/1", data={"quantity": 1})
    response = client.post("/checkout/", data={"name":"A User","email":"a@example.com","phone":"1234567890","address_line1":"1 Main St","city":"Pune","state":"MH","pincode":"411001"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Order received" in response.data
    assert b"Pending" in response.data
