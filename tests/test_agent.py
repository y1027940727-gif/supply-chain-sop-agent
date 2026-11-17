import pandas as pd
from src.agent import check_deterministic_alerts, verify_sop_citations

def test_deterministic_alert_gating():
    df = pd.DataFrame([
        {"part_id": "A1", "delay_days": 4, "defect_rate": 0.01, "stock_days": 10},
        {"part_id": "A2", "delay_days": 1, "defect_rate": 0.01, "stock_days": 10},
    ])
    alerts = check_deterministic_alerts(df)
    assert len(alerts) == 1
    assert alerts.iloc[0]["part_id"] == "A1"

def test_sop_verifier_blocks_fabricated_citations():
    retrieved = ["SOP-SC-101"]
    fake_output = "請啟動二供備援 [SOP-SC-101]，並進行跨廠區調撥 [SOP-SC-999]。"
    res = verify_sop_citations(fake_output, retrieved)
    assert res["is_grounded"] is False
    assert "SOP-SC-999" in res["fabricated"]
