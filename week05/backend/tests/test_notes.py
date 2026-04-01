def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_search_notes(client, seed_notes):
    r = client.get("/notes/search/", params={"q": "first"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any(
        "first" in n["title"].lower() or "first" in n["content"].lower() for n in data["items"]
    )


def test_search_case_insensitive(client, seed_notes):
    r = client.get("/notes/search/", params={"q": "FIRST"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1


def test_pagination(client, seed_notes):
    r = client.get("/notes/", params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


def test_pagination_page_out_of_range(client, seed_notes):
    r = client.get("/notes/", params={"page": 999, "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []


def test_sort_options(client, seed_notes):
    r = client.get("/notes/search/", params={"sort": "title_asc"})
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"sort": "title_desc"})
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"sort": "created_asc"})
    assert r.status_code == 200


def test_search_with_pagination(client, seed_notes):
    r = client.get("/notes/search/", params={"q": "note", "page": 1, "page_size": 1})
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert len(data["items"]) <= 1
