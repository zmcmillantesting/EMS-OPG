from ems_opg.database.models import Device, MACAddressPool, Order, OrderFailure


def seed_order_and_pool(seed, order_number="12345.6", quantity=5, mac_count=4):
    seed(
        Order(order_number=order_number, quantity=quantity),
        *[MACAddressPool(mac_address=f"AA:BB:CC:DD:EE:{i:02d}") for i in range(mac_count)],
    )


def advance_through_qr_steps(client):
    for _ in range(4):
        client.post("/api/workflow/next")


def run_to_awaiting_serial(client):
    client.put("/api/workflow/result", json={"result": "PASS"})


def run_full_pass(client, serial, mac1="AA:BB:CC:DD:EE:00"):
    run_to_awaiting_serial(client)
    client.put("/api/workflow/serial", json={"serial_number": serial})
    client.put("/api/workflow/mac-assign", json={"mac1": mac1})
    client.post("/api/workflow/mac-confirm")
    client.post("/api/workflow/verify-confirm")
    return client.post("/api/session/finish")


def test_session_start_requires_an_existing_order(client, seed):
    resp = client.post("/api/session/start", json={"operator": "4521", "order_number": "99999.9"})
    assert resp.status_code == 404


def test_full_pass_workflow_end_to_end(client, seed):
    seed_order_and_pool(seed)

    resp = client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    assert resp.status_code == 200
    assert resp.get_json()["session"]["state"] == "TESTING"

    advance_through_qr_steps(client)
    resp = client.get("/api/workflow")
    assert resp.get_json()["session"]["state"] == "AWAITING_RESULT"

    resp = client.put("/api/workflow/result", json={"result": "PASS"})
    assert resp.get_json()["session"]["state"] == "AWAITING_SERIAL"

    resp = client.put("/api/workflow/serial", json={"serial_number": "EM20260001"})
    assert resp.get_json()["session"]["state"] == "ASSIGNING_MAC"

    resp = client.put("/api/workflow/mac-assign", json={"mac1": "AA:BB:CC:DD:EE:00"})
    body = resp.get_json()
    assert body["session"]["mac1"] == "AA:BB:CC:DD:EE:00"
    assert body["session"]["mac2"] == "AA:BB:CC:DD:EE:01"

    resp = client.post("/api/workflow/mac-confirm")
    assert resp.get_json()["session"]["state"] == "VERIFYING_MAC"

    resp = client.post("/api/workflow/verify-confirm")
    assert resp.get_json()["session"]["state"] == "READY_TO_SAVE"

    resp = client.post("/api/session/finish")
    assert resp.status_code == 200
    # Looped straight back to the next board under the same operator/order.
    assert resp.get_json()["session"]["state"] == "TESTING"

    resp = client.get("/api/devices/EM20260001?order_number=12345.6")
    device = resp.get_json()["device"]
    assert device["test_result"] == "PASS"
    assert device["ethaddr_id"] == "AA:BB:CC:DD:EE:00"
    assert device["used"] is True


def test_workflow_serial_rejects_malformed_serial(client, seed):
    seed_order_and_pool(seed)
    client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    advance_through_qr_steps(client)
    run_to_awaiting_serial(client)

    resp = client.put("/api/workflow/serial", json={"serial_number": "not-a-serial"})
    assert resp.status_code == 400


def test_workflow_serial_rejects_a_duplicate_within_the_same_order(client, seed):
    seed_order_and_pool(seed)
    client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    advance_through_qr_steps(client)
    run_full_pass(client, "EM20260001", mac1="AA:BB:CC:DD:EE:00")

    client.post("/api/session/start", json={"operator": "4522", "order_number": "12345.6"})
    advance_through_qr_steps(client)
    run_to_awaiting_serial(client)

    resp = client.put("/api/workflow/serial", json={"serial_number": "EM20260001"})
    assert resp.status_code == 409


def test_fail_workflow_records_an_order_failure_and_creates_no_device(client, seed, test_db):
    seed_order_and_pool(seed)

    client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    advance_through_qr_steps(client)

    resp = client.put("/api/workflow/result", json={
        "result": "FAIL", "notes": "fails -LL during functional test",
    })
    assert resp.get_json()["session"]["state"] == "READY_TO_SAVE"

    resp = client.post("/api/session/finish")
    assert resp.status_code == 200
    assert resp.get_json()["session"]["state"] == "TESTING"

    session = test_db()
    try:
        assert session.query(Device).count() == 0
        failures = session.query(OrderFailure).all()
        assert len(failures) == 1
        assert failures[0].order_number == "12345.6"
        assert failures[0].operator == "4521"
        assert failures[0].reason == "fails -LL during functional test"
    finally:
        session.close()


def test_fail_result_requires_notes(client, seed):
    seed_order_and_pool(seed)
    client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    advance_through_qr_steps(client)

    resp = client.put("/api/workflow/result", json={"result": "FAIL", "notes": ""})
    assert resp.status_code == 400


def test_orders_post_creates_an_order(client, seed):
    resp = client.post("/api/orders", json={"order_number": "12345.6", "quantity": 10})
    assert resp.status_code == 201

    resp = client.get("/api/orders")
    orders = resp.get_json()["orders"]
    assert orders == [{"order_number": "12345.6", "quantity": 10, "passed": 0, "remaining": 10}]


def test_orders_get_reports_passed_and_remaining(client, seed):
    seed_order_and_pool(seed, quantity=3)
    client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    advance_through_qr_steps(client)
    run_full_pass(client, "EM20260001")

    resp = client.get("/api/orders")
    order = resp.get_json()["orders"][0]
    assert order["passed"] == 1
    assert order["remaining"] == 2


def test_delete_order_blocked_when_devices_exist(client, seed):
    seed_order_and_pool(seed)
    seed(Device(order_number="12345.6", serial_number="EM20260001", operator="4521"))

    resp = client.delete("/api/orders/12345.6", json={"operator": "4521"})
    assert resp.status_code == 409


def test_delete_order_succeeds_when_empty(client, seed):
    seed(Order(order_number="12345.6", quantity=5))

    resp = client.delete("/api/orders/12345.6", json={"operator": "4521"})
    assert resp.status_code == 200


def test_update_device_requires_order_serial_and_mac1(client, seed):
    seed_order_and_pool(seed)
    seed(Device(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        ethaddr_id="AA:BB:CC:DD:EE:00", eth1addr_id="AA:BB:CC:DD:EE:01",
    ))

    resp = client.put("/api/devices/EM20260001", json={
        "order_number": "12345.6", "serial_number": "EM20260001", "operator": "4521",
        "reason": "typo fix",
    })
    assert resp.status_code == 400


def test_update_device_corrects_serial_and_mac(client, seed):
    seed_order_and_pool(seed, mac_count=4)
    seed(Device(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        ethaddr_id="AA:BB:CC:DD:EE:00", eth1addr_id="AA:BB:CC:DD:EE:01",
    ))

    resp = client.put("/api/devices/EM20260001", json={
        "order_number": "12345.6", "serial_number": "EM20260009", "operator": "4521",
        "mac1": "AA:BB:CC:DD:EE:00", "mac2": "AA:BB:CC:DD:EE:01",
        "reason": "mis-scanned serial",
    })
    assert resp.status_code == 200
    assert resp.get_json()["device"]["serial_number"] == "EM20260009"


def test_reset_device_mac_releases_pool_and_deletes_the_device(client, seed):
    seed_order_and_pool(seed)
    client.post("/api/session/start", json={"operator": "4521", "order_number": "12345.6"})
    advance_through_qr_steps(client)
    run_full_pass(client, "EM20260001")

    resp = client.post("/api/devices/EM20260001/reset-mac", json={
        "reason": "wrong labels applied", "current_order_number": "12345.6",
    })
    assert resp.status_code == 200

    resp = client.get("/api/devices/EM20260001?order_number=12345.6")
    assert resp.status_code == 404

    resp = client.get("/api/mac-pool")
    pool = {r["mac_address"]: r["used"] for r in resp.get_json()["records"]}
    assert pool["AA:BB:CC:DD:EE:00"] is False
    assert pool["AA:BB:CC:DD:EE:01"] is False