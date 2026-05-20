def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_get_single_item(client):
    r = client.post("/action-items/", json={"description": "Get me"})
    item_id = r.json()["id"]

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    assert r.json()["description"] == "Get me"


def test_get_item_not_found(client):
    r = client.get("/action-items/99999")
    assert r.status_code == 404


def test_delete_item(client):
    r = client.post("/action-items/", json={"description": "Delete me"})
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_delete_item_not_found(client):
    r = client.delete("/action-items/99999")
    assert r.status_code == 404


def test_reopen_item(client):
    r = client.post("/action-items/", json={"description": "Reopen me"})
    item_id = r.json()["id"]

    r = client.put(f"/action-items/{item_id}/complete")
    assert r.json()["completed"] is True

    r = client.put(f"/action-items/{item_id}/reopen")
    assert r.status_code == 200
    assert r.json()["completed"] is False


def test_reopen_already_open(client):
    r = client.post("/action-items/", json={"description": "Open item"})
    item_id = r.json()["id"]

    r = client.put(f"/action-items/{item_id}/reopen")
    assert r.status_code == 200
    assert r.json()["completed"] is False


def test_create_item_empty_description(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422


def test_patch_item_empty_description(client):
    r = client.post("/action-items/", json={"description": "X"})
    item_id = r.json()["id"]
    r = client.patch(f"/action-items/{item_id}", json={"description": ""})
    assert r.status_code == 422


def test_list_items_invalid_sort(client):
    r = client.get("/action-items/", params={"sort": "bogus"})
    assert r.status_code == 400


def test_list_items_negative_skip(client):
    r = client.get("/action-items/", params={"skip": -1})
    assert r.status_code == 422


def test_list_items_zero_limit(client):
    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422


