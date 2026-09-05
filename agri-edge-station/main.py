import uvicorn
import logging
import signal
import sys
import database
from mock_sensor import FieldSensorSimulator
from sync_worker import CloudSyncWorker
from server import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("agri_edge_main")

def main():
    logger.info("=" * 65)
    logger.info("  AGRISMART TIER 2: OFFLINE LOCAL EDGE GATEWAY STATION")
    logger.info("  Zero-Internet Local Hotspot (10.42.0.1:8000 / localhost:8000)")
    logger.info("=" * 65)

    # 1. Initialize SQLite Database and Actuators
    database.init_db()
    logger.info("Initialized local SQLite offline buffer (agri_edge.db)")

    # 2. Start Background Mock Sensor Simulator (5s interval)
    simulator = FieldSensorSimulator()
    simulator_thread = simulator.start_background(interval_seconds=5.0)
    logger.info("Started Mock Sensor Simulator thread (5s polling)")

    # 3. Start Background Cloud Sync Worker (10s interval)
    sync_worker = CloudSyncWorker()
    sync_thread = sync_worker.start_background(interval_seconds=10.0)
    logger.info("Started Cloud Sync Worker thread (10s sync batch to Tier 3 Cloud)")

    def handle_shutdown(signum, frame):
        logger.info("Received termination signal. Shutting down AgriSmart Edge...")
        simulator.stop()
        sync_worker.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # 4. Start FastAPI / Uvicorn Server
    logger.info("Launching FastAPI Edge Server on http://0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
        access_log=False
    )

if __name__ == "__main__":
    main()
