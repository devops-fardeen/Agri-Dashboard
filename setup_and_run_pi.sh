#!/bin/bash
# =====================================================================
# AgriSmart Raspberry Pi 5 All-in-One Setup & Run Script
# =====================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "  🌱 AgriSmart Edge Station & AI Engine (Raspberry Pi 5)"
echo "=========================================================="

# 1. Install system prerequisites
echo "[1/4] Installing system prerequisites..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv libgl1 libglib2.0-0 git curl sqlite3

# 2. Setup Python virtual environment
echo "[2/4] Setting up Python virtual environment (~/agri-venv)..."
if [ ! -d "$HOME/agri-venv" ]; then
    python3 -m venv "$HOME/agri-venv"
fi
source "$HOME/agri-venv/bin/activate"

# 3. Install Python Dependencies
echo "[3/4] Installing Python AI & Gateway dependencies..."
pip install --upgrade pip
pip install -r "$DIR/dashboard-ai-modals/requirements.txt"
pip install -r "$DIR/agri-edge-station/requirements.txt"

# 4. Launch Services
echo "[4/4] Starting AI Engine (:5000) & Edge Station Gateway (:8000)..."

cd "$DIR/dashboard-ai-modals"
python3 main.py > "$DIR/ai_engine.log" 2>&1 &
AI_PID=$!
echo "✓ AI Model Engine started (PID: $AI_PID on Port 5000)"

cd "$DIR/agri-edge-station"
python3 main.py > "$DIR/edge_station.log" 2>&1 &
EDGE_PID=$!
echo "✓ Edge Station Gateway started (PID: $EDGE_PID on Port 8000)"

cd "$DIR"

IP_ADDR=$(hostname -I | awk '{print $1}')
echo ""
echo "=========================================================="
echo "  🎉 ALL SERVICES ARE RUNNING!"
echo "  📱 Open on your Phone / Laptop browser:"
echo "     👉 http://${IP_ADDR}:8000"
echo "     👉 http://raspberrypi.local:8000"
echo "=========================================================="
echo "Logs are available at:"
echo "  - ai_engine.log"
echo "  - edge_station.log"
echo "Press Ctrl+C to stop all services."

trap "echo 'Stopping services...'; kill $AI_PID $EDGE_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
