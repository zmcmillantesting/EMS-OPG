from pathlib import Path

from scripts.load_database import load_csv


def test_load_csv_uses_mac_address_column(tmp_path: Path):
    csv_path = tmp_path / "macs.csv"
    csv_path.write_text(
        "id,order_number,serial_number,mac_address,used,test_result,timestamp,operator,created_at,updated_at,post_testing_changes\n"
        "1,,SN001,00:13:C6:13:3F:00,False,False,,,,,\n"
        "2,,SN002,00:13:C6:13:3F:01,False,False,,,,,\n",
        encoding="utf-8",
    )

    assert load_csv(csv_path) == [
        "00:13:C6:13:3F:00",
        "00:13:C6:13:3F:01",
    ]
