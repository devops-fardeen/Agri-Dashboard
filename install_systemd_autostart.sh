#!/bin/bash
# =====================================================================
# AgriSmart Raspberry Pi 5 Systemd Autostart Installer
# =====================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER=$(whoami)
VENV_PYTHON="$HOME/agri-venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "⚠️ Python virtual environment not found at $HOME/agri-venv"
    echo "Please run ./setup_and_run_pi.sh first to build the environment."
    exit 1
fi

echo "=========================================================="
echo "  Setting up Systemd Autostart Services for AgriSmart"
echo "=========================================================="

# 1. Create AI Models service
sudo bash -c "cat <<EOF > /etc/systemd/system/agri-ai.service
[Unit]
Description=AgriSmart AI Model Engine (Port 5000)
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$DIR/dashboard-ai-modals
ExecStart=$VENV_PYTHON main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

# 2. Create Edge Station service
sudo bash -c "cat <<EOF > /etc/systemd/system/agri-edge.service
[Unit]
Description=AgriSmart Offline Edge Gateway (Port 8000)
After=network.target agri-ai.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$DIR/agri-edge-station
ExecStart=$VENV_PYTHON main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

# 3. Reload systemd, enable and start services
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling services on boot..."
sudo systemctl enable agri-ai.service
sudo systemctl enable agri-edge.service

echo "Starting services now..."
sudo systemctl restart agri-ai.service
sudo systemctl restart agri-edge.service

IP_ADDR=$(hostname -I | awk '{print $1}')
echo ""
echo "=========================================================="
echo "  ✅ AUTOSTART INSTALLED SUCCESSFULLY!"
echo "  The Edge Station will now start automatically whenever Pi boots."
echo ""
echo "  📱 Access Dashboard at:"
echo "     👉 http://${IP_ADDR}:8000"
echo "     👉 http://raspberrypi.local:8000"
echo ""
echo "  Useful Commands:"
echo "    - Check Status: sudo systemctl status agri-edge.service"
echo "    - View Logs:    sudo journalctl -u agri-edge.service -f"
echo "    - Restart:      sudo systemctl restart agri-edge.service"
echo "=========================================================="
