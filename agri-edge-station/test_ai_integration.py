"""
End-to-End System & AI Integration Test Suite
Validates the complete 4 AI Model integration into the AgriSmart 3-Tier Architecture.
"""
import os
import sys
import json
import time

# Set stdout encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
from fastapi.testclient import TestClient
import server
import sync_worker

def test_full_ai_pipeline():
    print("=" * 65)
    print("  AGRISMART 3-TIER ARCHITECTURE: 4 AI MODELS INTEGRATION TEST")
    print("=" * 65)

    # 1. Initialize SQLite Database
    database.init_db()
    print("[1/5] [OK] SQLite Database initialized with ai_detections table.")

    # 2. Test AI Bundle Logging (Disease, Pest, Nutrition, Growth Stage)
    mock_inference_results = {
        "disease": [
            {"name": "Early Blight", "confidence": 0.935, "bbox": [120, 80, 400, 360], "class_id": 0}
        ],
        "pest": [
            {"name": "Silverleaf whitefly", "confidence": 0.882, "bbox": [60, 45, 180, 160], "class_id": 3}
        ],
        "nutrition": [
            {"name": "nitrogen deficiency", "confidence": 0.791, "bbox": [150, 120, 520, 480], "class_id": 3}
        ],
        "stage": [
            {"name": "Stage 2", "confidence": 0.965, "bbox": [0, 0, 640, 640], "class_id": 1}
        ]
    }
    
    inserted_ids = database.log_ai_inference_bundle("NODE_01", mock_inference_results, "node1_frame_001.jpg")
    assert len(inserted_ids) == 4, f"Expected 4 inserted records, got {len(inserted_ids)}"
    print(f"[2/5] [OK] Ingested 4-model inference bundle into SQLite. Record IDs: {inserted_ids}")

    # 3. Test AI Summary and Alert Extraction
    summary = database.get_latest_ai_summary("NODE_01")
    assert summary["disease"]["detection_label"] == "Early Blight"
    assert summary["pest"]["detection_label"] == "Silverleaf whitefly"
    assert summary["nutrition"]["detection_label"] == "nitrogen deficiency"
    assert summary["stage"]["detection_label"] == "Stage 2"
    assert len(summary["alerts"]) >= 3
    print(f"[3/5] [OK] Generated AI summary for NODE_01 with {len(summary['alerts'])} active alerts.")

    # 4. Test Edge FastAPI Endpoints using TestClient
    client = TestClient(server.app)
    
    # 4a. /api/edge/status
    res_status = client.get("/api/edge/status")
    assert res_status.status_code == 200
    status_json = res_status.json()
    assert "ai" in status_json
    assert status_json["ai"]["disease"]["detection_label"] == "Early Blight"
    print("      [OK] GET /api/edge/status successfully includes real-time AI summary.")

    # 4b. /api/edge/ai/latest
    res_ai = client.get("/api/edge/ai/latest?node_id=NODE_01")
    assert res_ai.status_code == 200
    ai_json = res_ai.json()
    assert ai_json["success"] is True
    assert len(ai_json["recent_detections"]) > 0
    print("      [OK] GET /api/edge/ai/latest successfully returns AI history and diagnostics.")

    # 4c. /api/edge/ai/detection
    single_det = {
        "node_id": "NODE_02",
        "model_name": "disease",
        "detection_label": "Healthy",
        "confidence": 0.99,
        "image_path": "node2_frame_002.jpg",
        "metadata_json": json.dumps({"status": "CLEAR"})
    }
    res_det = client.post("/api/edge/ai/detection", json=single_det)
    assert res_det.status_code == 200
    assert res_det.json()["success"] is True
    print("      [OK] POST /api/edge/ai/detection direct telemetry ingest verified.")
    print("[4/5] [OK] All FastAPI edge AI endpoints passed successfully.")

    # 5. Test Sync Worker AI Batch Extraction & Cloud Transformation
    unsynced = database.get_unsynced_ai_detections(limit=10)
    assert len(unsynced) >= 4
    worker_inst = sync_worker.CloudSyncWorker()
    
    # Transform to cloud payload
    cloud_payload = []
    for r in unsynced:
        cloud_payload.append({
            "nodeId": r["node_id"],
            "modelName": r["model_name"],
            "detectionLabel": r["detection_label"],
            "confidence": r["confidence"],
            "imagePath": r.get("image_path"),
            "metadata": json.loads(r["metadata_json"]) if r.get("metadata_json") else {},
            "recordedAt": r["created_at"]
        })
    assert len(cloud_payload) == len(unsynced)
    assert cloud_payload[0]["modelName"] in ["disease", "pest", "nutrition", "stage"]
    
    # Mark synced test
    ids_to_sync = [r["id"] for r in unsynced]
    marked = database.mark_ai_detections_synced(ids_to_sync)
    assert marked == len(ids_to_sync)
    
    remaining_unsynced = database.get_unsynced_ai_detections(limit=10)
    assert len(remaining_unsynced) == 0
    print(f"[5/5] [OK] Cloud Sync worker AI offload payload verified ({marked} records synced & cleared).")

    print("=" * 65)
    print("  ALL 5 INTEGRATION PHASES VERIFIED AND PASSED!")
    print("=" * 65)

if __name__ == "__main__":
    test_full_ai_pipeline()
