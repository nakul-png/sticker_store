def test_product_list_and_detail(client):
    assert client.get("/products/").status_code == 200
    assert client.get("/products/test-sticker").status_code == 200
    assert client.get("/products/missing").status_code == 404
