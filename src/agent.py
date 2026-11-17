import re
import pandas as pd

# 模擬工廠/供應鏈標準作業程序知識庫 (SOP Knowledge Base)
SOP_DATABASE = {
    "SOP-SC-101": {
        "title": "關鍵零組件交期延遲應變規範",
        "content": "當單一供應商交期延遲超過 3 個工作天時，採購系統需自動觸發二供（Second Source）備援庫存調度，並通知生管調整排程。"
    },
    "SOP-SC-102": {
        "title": "晶圓與基板來料異常隔離程序",
        "content": "若來料檢驗（IQC）不良率超過 2%，品管人員須立即凍結該批次（Lot Hold），並於 24 小時內啟動供應商 8D 矯正預防報告。"
    },
    "SOP-SC-103": {
        "title": "安全庫存水位跌破預警處理",
        "content": "當安全庫存低於 7 天用量時，ERP 需自動產生緊急請購單（PR），並由資材主管進行加急空運審批。"
    }
}

def check_deterministic_alerts(shipment_df: pd.DataFrame, max_delay_days: int = 3) -> pd.DataFrame:
    """確定性規則引擎：卡控交期延遲或不良率超標之異常工單"""
    return shipment_df[
        (shipment_df["delay_days"] > max_delay_days) | (shipment_df["defect_rate"] > 0.02)
    ].copy()

def retrieve_relevant_sops(alert_row: pd.Series) -> list:
    """根據異常類型檢索對應的 SOP 編號"""
    retrieved_ids = []
    if alert_row["delay_days"] > 3:
        retrieved_ids.append("SOP-SC-101")
    if alert_row["defect_rate"] > 0.02:
        retrieved_ids.append("SOP-SC-102")
    if alert_row["stock_days"] < 7:
        retrieved_ids.append("SOP-SC-103")
    return retrieved_ids

def verify_sop_citations(generated_text: str, retrieved_ids: list) -> dict:
    """確定性引用驗證器：攔截任何未被檢索到的 SOP 編號"""
    cited_ids = re.findall(r"\[(SOP-SC-\d+)\]", generated_text)
    valid = [cid for cid in cited_ids if cid in retrieved_ids]
    fabricated = [cid for cid in cited_ids if cid not in retrieved_ids]
    return {
        "cited": cited_ids,
        "valid": valid,
        "fabricated": fabricated,
        "is_grounded": len(fabricated) == 0 and len(cited_ids) > 0
    }

def generate_grounded_action_plan(alert_row: pd.Series, retrieved_ids: list) -> str:
    """以模板產生處置建議（每句附帶檢索到的 SOP 編號）。目前未接 LLM。"""
    actions = []
    for sid in retrieved_ids:
        sop = SOP_DATABASE[sid]
        actions.append(f"針對料號 {alert_row['part_id']}，依據《{sop['title']}》執行：{sop['content']} [{sid}]")
    return " ".join(actions) if actions else "目前無觸發異常處置規則。"

if __name__ == "__main__":
    mock_data = pd.DataFrame([
        {"part_id": "IC-MCU-882", "delay_days": 5, "defect_rate": 0.005, "stock_days": 10},
        {"part_id": "PCB-SUB-104", "delay_days": 1, "defect_rate": 0.035, "stock_days": 5},
        {"part_id": "CAP-MLCC-09", "delay_days": 0, "defect_rate": 0.001, "stock_days": 20},
    ])
    alerts = check_deterministic_alerts(mock_data)
    print(f"偵測到 {len(alerts)} 筆異常工單：\n")
    for _, row in alerts.iterrows():
        sops = retrieve_relevant_sops(row)
        plan = generate_grounded_action_plan(row, sops)
        check = verify_sop_citations(plan, sops)
        print(f"工單料號: {row['part_id']} | 引用驗證: {check['is_grounded']}")
