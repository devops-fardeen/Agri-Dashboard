"""
AprilTag Vision Guidance System for AgriSmart Master Node Base
==============================================================
Mounted: Raspberry Pi NoIR V2 Camera on Master Node base corner at ~1.5m height
Base Dimensions: 2.0m x 1.5m
Tag Standard: tag36h11

AprilTag Map (6 Targets - from official PDF):
  ID 0: ROVER (Mounted flat and square on Rover chassis top)
  ID 1: DOCK (Charging Station / Default Position)
  ID 2: FIELD_A_ENTRY
  ID 3: FIELD_A_EXIT
  ID 4: FIELD_B_ENTRY
  ID 5: FIELD_B_EXIT

Guidance Workflow:
  1. User triggers navigation (e.g. Patrol Field B).
  2. The system locks initial positions of static tags (Field B Entry, etc.) so tag occlusion
     by the rover body never loses the target coordinates.
  3. Pre-entry approach waypoint: Computes an approach waypoint 20 cm in front of the entry tag.
  4. Closed-loop Visual Servoing:
     - Detects Rover (Tag 1) center (x, y) and heading angle theta.
     - Controls Rover steering (LEFT / RIGHT / FORWARD) and speed towards 20cm pre-entry point.
     - Slowly navigates through the entry waypoint.
  5. Once arrived at entry:
     - Signals "ARRIVED".
     - Switches Rover to firmware AUTO patrol mode (`auto_on`).
  6. On return / patrol completion (detected by exit tag or schedule):
     - Visually guides Rover back to Tag 0 (Charging Station / Dock).
     - Locks in dock alignment and signals "DOCKED".
"""

import os
import cv2
import math
import time
import json
import logging
import threading
import numpy as np
from typing import Dict, Optional, Tuple, Any
import requests

logger = logging.getLogger("apriltag_guidance")

# Try importing pupil_apriltags or apriltag or opencv aruco as fallback
APRILTAG_LIB_AVAILABLE = False
try:
    from pupil_apriltags import Detector
    detector_instance = Detector(
        families="tag36h11",
        nthreads=2,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0
    )
    APRILTAG_LIB_AVAILABLE = "pupil"
except ImportError:
    try:
        import apriltag
        detector_instance = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11"))
        APRILTAG_LIB_AVAILABLE = "apriltag"
    except ImportError:
        detector_instance = None
        APRILTAG_LIB_AVAILABLE = False
        logger.warning("pupil-apriltags/apriltag library not found. Will use OpenCV Aruco tag36h11 fallback or simulated tag tracking.")

# AprilTag Target IDs (Matching PDF Sheet)
TAG_ROVER = 0
TAG_CHARGING_DOCK = 1
TAG_FIELD_A_ENTRY = 2
TAG_FIELD_A_EXIT = 3
TAG_FIELD_B_ENTRY = 4
TAG_FIELD_B_EXIT = 5

TAG_NAMES = {
    TAG_ROVER: "ROVER",
    TAG_CHARGING_DOCK: "DOCK",
    TAG_FIELD_A_ENTRY: "FIELD_A_ENTRY",
    TAG_FIELD_A_EXIT: "FIELD_A_EXIT",
    TAG_FIELD_B_ENTRY: "FIELD_B_ENTRY",
    TAG_FIELD_B_EXIT: "FIELD_B_EXIT"
}

class AprilTagGuidanceController:
    """Controls Pi Camera capture, AprilTag 2D localization, and Visual Servoing to Rover."""

    def __init__(self, rover_ip: str = "10.208.70.197"):
        self.rover_ip = rover_ip
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # State & Missions
        # States: IDLE, NAVIGATING_TO_PRE_ENTRY, NAVIGATING_TO_ENTRY, AUTO_PATROLLING, NAVIGATING_TO_DOCK, DOCKED
        self.state = "IDLE"
        self.mission_target = None  # "FIELD_A" or "FIELD_B"
        self.status_message = "AprilTag Vision Guidance System Standby"
        
        # Stored Tag Positions in Base Pixel Coordinates & Homography Metrics
        # Structure: {tag_id: {"x": float, "y": float, "angle": float, "last_seen": float, "locked": bool}}
        self.tag_positions: Dict[int, Dict[str, Any]] = {}
        self.locked_waypoints: Dict[str, Dict[str, float]] = {}
        
        # Master Base Dimensions: 2.0m x 1.5m
        self.base_width_meters = 2.0
        self.base_height_meters = 1.5
        
        # Real-time metrics
        self.rover_pose = {"x": 0.0, "y": 0.0, "heading_deg": 0.0, "visible": False}
        self.distance_to_target_cm = 0.0
        self.heading_error_deg = 0.0
        self.last_frame = None
        self.last_annotated_frame = None
        
        # Navigation tolerances
        self.approach_offset_cm = 20.0  # Stop 20cm in front before final docking/entry
        self.target_reached_threshold_cm = 8.0 # Within 8cm is marked reached
        self.angle_tolerance_deg = 15.0

    def start(self):
        """Starts background vision capture & guidance loop."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._vision_loop, daemon=True)
        self.thread.start()
        logger.info("AprilTag Vision Guidance Controller started on background thread.")

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        logger.info("AprilTag Vision Guidance Controller stopped.")

    def set_rover_ip(self, ip: str):
        self.rover_ip = ip

    def lock_tag_positions(self):
        """Snapshots and locks positions of static field tags so occlusions do not disrupt navigation."""
        with self.lock:
            for tag_id, data in self.tag_positions.items():
                if tag_id != TAG_ROVER:
                    data["locked"] = True
                    logger.info(f"Locked position for AprilTag {tag_id} ({TAG_NAMES.get(tag_id, 'UNKNOWN')}): x={data['x']:.1f}, y={data['y']:.1f}")

    def start_mission(self, field: str = "FIELD_B") -> Dict[str, Any]:
        """Initiates autonomous guided patrol mission to specified field."""
        field_clean = "FIELD_B" if "B" in field.upper() else "FIELD_A"
        self.mission_target = field_clean
        
        # 1. Lock static tags immediately on user click
        self.lock_tag_positions()
        
        # 2. Check if we have tag positions (or fallback defaults)
        entry_tag_id = TAG_FIELD_B_ENTRY if field_clean == "FIELD_B" else TAG_FIELD_A_ENTRY
        with self.lock:
            self.state = "NAVIGATING_TO_PRE_ENTRY"
            self.status_message = f"Aligning & driving rover to 20cm front approach for {field_clean} Entry"
        
        logger.info(f"Mission started: Guide Rover to {field_clean} (Tag {entry_tag_id})")
        return {
            "success": True,
            "mission": field_clean,
            "state": self.state,
            "target_tag_id": entry_tag_id,
            "message": self.status_message
        }

    def cancel_mission(self):
        """Stops active mission and halts rover."""
        with self.lock:
            self.state = "IDLE"
            self.status_message = "Mission cancelled. Rover stopped."
        self._send_rover_cmd("stop")

    def return_to_dock(self) -> Dict[str, Any]:
        """Guides rover back to Charging Station / Dock (Tag 0)."""
        with self.lock:
            self.state = "NAVIGATING_TO_DOCK"
            self.status_message = "Guiding Rover to Charging Station / Dock (Tag 0)"
        logger.info("Mission started: Guide Rover back to Charging Station (Tag 0)")
        return {
            "success": True,
            "state": self.state,
            "message": self.status_message
        }

    def _send_rover_cmd(self, move_cmd: str):
        """Dispatches movement command to Rover ESP32 WebServer."""
        try:
            requests.get(f"http://{self.rover_ip}/cmd?move={move_cmd}", timeout=1.0)
        except Exception as e:
            logger.debug(f"Failed to transmit move command {move_cmd} to {self.rover_ip}: {e}")

    def _send_rover_speed(self, speed: int):
        """Sets Rover motor speed (PWM 60-255)."""
        try:
            requests.get(f"http://{self.rover_ip}/speed?value={speed}", timeout=1.0)
        except Exception:
            pass

    def _detect_apriltags(self, gray_frame: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """Detects AprilTags and computes center, corners, and heading vector in frame."""
        detected = {}
        h, w = gray_frame.shape[:2]

        if APRILTAG_LIB_AVAILABLE == "pupil" and detector_instance:
            tags = detector_instance.detect(gray_frame)
            for t in tags:
                tag_id = int(t.tag_id)
                center_x, center_y = float(t.center[0]), float(t.center[1])
                corners = t.corners
                # Heading vector from corner[0] -> corner[1]
                dx = corners[1][0] - corners[0][0]
                dy = corners[1][1] - corners[0][1]
                angle_deg = math.degrees(math.atan2(dy, dx))
                detected[tag_id] = {
                    "x": center_x,
                    "y": center_y,
                    "angle": angle_deg,
                    "corners": corners.tolist(),
                    "last_seen": time.time()
                }
        elif APRILTAG_LIB_AVAILABLE == "apriltag" and detector_instance:
            tags = detector_instance.detect(gray_frame)
            for t in tags:
                tag_id = int(t.tag_id)
                center_x, center_y = float(t.center[0]), float(t.center[1])
                corners = t.corners
                dx = corners[1][0] - corners[0][0]
                dy = corners[1][1] - corners[0][1]
                angle_deg = math.degrees(math.atan2(dy, dx))
                detected[tag_id] = {
                    "x": center_x,
                    "y": center_y,
                    "angle": angle_deg,
                    "corners": corners.tolist(),
                    "last_seen": time.time()
                }
        else:
            # Fallback: OpenCV cv2.aruco with tag36h11 dictionary
            try:
                aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
                parameters = cv2.aruco.DetectorParameters()
                corners, ids, _ = cv2.aruco.detectMarkers(gray_frame, aruco_dict, parameters=parameters)
                if ids is not None:
                    for i, tag_id_arr in enumerate(ids):
                        tag_id = int(tag_id_arr[0])
                        c = corners[i][0]
                        center_x = float(np.mean(c[:, 0]))
                        center_y = float(np.mean(c[:, 1]))
                        dx = c[1][0] - c[0][0]
                        dy = c[1][1] - c[0][1]
                        angle_deg = math.degrees(math.atan2(dy, dx))
                        detected[tag_id] = {
                            "x": center_x,
                            "y": center_y,
                            "angle": angle_deg,
                            "corners": c.tolist(),
                            "last_seen": time.time()
                        }
            except Exception:
                pass

        return detected

    def _get_target_waypoint(self, target_tag_id: int, approach_offset_cm: float = 0.0) -> Optional[Tuple[float, float]]:
        """Calculates world pixel coordinate of target or pre-entry waypoint (offset in front)."""
        tag_info = self.tag_positions.get(target_tag_id)
        if not tag_info:
            return None
            
        tx, ty = tag_info["x"], tag_info["y"]
        if approach_offset_cm <= 0:
            return (tx, ty)
            
        # Scale: Approximate 2.0m x 1.5m base on 640x480 frame -> ~3.0 pixels per cm
        pixels_per_cm = 2.8
        offset_pixels = approach_offset_cm * pixels_per_cm
        
        # If tag has heading, approach in front of tag (-y or normal vector)
        tag_angle = tag_info.get("angle", 0.0)
        # Approach vector pointing outwards from tag
        angle_rad = math.radians(tag_angle + 90)
        wx = tx - offset_pixels * math.cos(angle_rad)
        wy = ty - offset_pixels * math.sin(angle_rad)
        return (wx, wy)

    def _vision_loop(self):
        """Continuously captures frames from Pi camera, detects tags, and executes visual servoing."""
        # Open Pi Camera / VideoCapture
        cap = None
        try:
            # Try camera index 0 (Pi NoIR V2 / V4L2)
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        except Exception:
            cap = None

        logger.info(f"Vision Capture loop initialized (Camera opened: {cap is not None and cap.isOpened()})")

        last_control_time = time.time()

        while self.running:
            frame = None
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    frame = None

            # Fallback synthetic frame generation for testing/simulation if camera is offline
            if frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                # Draw Master Node base outline (2.0m x 1.5m)
                cv2.rectangle(frame, (40, 40), (600, 440), (40, 40, 50), -1)
                cv2.rectangle(frame, (40, 40), (600, 440), (0, 200, 100), 2)
                cv2.putText(frame, "Pi NoIR V2 Base View (Simulated/Overlay)", (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected = self._detect_apriltags(gray)

            # Update tag position dictionary
            with self.lock:
                now = time.time()
                for tag_id, data in detected.items():
                    # If static tag is locked, keep locked coordinates unless explicitly updated
                    if tag_id in self.tag_positions and self.tag_positions[tag_id].get("locked", False):
                        self.tag_positions[tag_id]["last_seen"] = now
                    else:
                        self.tag_positions[tag_id] = {
                            "x": data["x"],
                            "y": data["y"],
                            "angle": data["angle"],
                            "last_seen": now,
                            "locked": False
                        }

                # Update Rover Pose if Tag 1 visible
                if TAG_ROVER in detected:
                    r_data = detected[TAG_ROVER]
                    self.rover_pose = {
                        "x": r_data["x"],
                        "y": r_data["y"],
                        "heading_deg": r_data["angle"],
                        "visible": True
                    }
                else:
                    # Keep last position but mark visibility
                    self.rover_pose["visible"] = (now - self.tag_positions.get(TAG_ROVER, {}).get("last_seen", 0)) < 1.0

            # Execute visual servoing state machine (rate-limited to 10Hz)
            if now - last_control_time >= 0.1:
                last_control_time = now
                self._step_state_machine()

            # Annotate Frame for Real-time Dashboard Stream
            annotated = self._annotate_frame(frame.copy(), detected)
            self.last_frame = frame
            self.last_annotated_frame = annotated

            time.sleep(0.03)  # ~30 FPS loop

        if cap:
            cap.release()

    def _step_state_machine(self):
        """Executes navigation logic based on current state and visual tag feedback."""
        with self.lock:
            state = self.state
            mission = self.mission_target

        if state == "IDLE":
            return

        # Target Tag ID based on state
        target_tag_id = None
        approach_dist_cm = 0.0

        if state == "NAVIGATING_TO_PRE_ENTRY":
            target_tag_id = TAG_FIELD_B_ENTRY if mission == "FIELD_B" else TAG_FIELD_A_ENTRY
            approach_dist_cm = self.approach_offset_cm  # 20cm far in front
        elif state == "NAVIGATING_TO_ENTRY":
            target_tag_id = TAG_FIELD_B_ENTRY if mission == "FIELD_B" else TAG_FIELD_A_ENTRY
            approach_dist_cm = 0.0 # Direct entry
        elif state == "NAVIGATING_TO_DOCK":
            target_tag_id = TAG_CHARGING_DOCK
            approach_dist_cm = 0.0

        if target_tag_id is None:
            return

        waypoint = self._get_target_waypoint(target_tag_id, approach_dist_cm)
        if not waypoint:
            # Default fallback positions if tags not yet physically scanned
            fallback_coords = {
                TAG_CHARGING_DOCK: (100, 240),
                TAG_FIELD_A_ENTRY: (520, 120),
                TAG_FIELD_A_EXIT: (520, 200),
                TAG_FIELD_B_ENTRY: (520, 320),
                TAG_FIELD_B_EXIT: (520, 400),
            }
            waypoint = fallback_coords.get(target_tag_id, (320, 240))

        # Rover position
        rx, ry = self.rover_pose["x"], self.rover_pose["y"]
        r_heading = self.rover_pose["heading_deg"]
        
        # If rover position is unknown, fallback to center
        if rx == 0 and ry == 0:
            rx, ry = 160, 240

        # Vector from Rover -> Target Waypoint
        tx, ty = waypoint
        dx = tx - rx
        dy = ty - ry
        dist_pixels = math.sqrt(dx * dx + dy * dy)
        dist_cm = dist_pixels / 2.8  # ~2.8 pixels per cm
        self.distance_to_target_cm = round(dist_cm, 1)

        # Desired Heading Angle towards target
        desired_angle_deg = math.degrees(math.atan2(dy, dx))
        
        # Heading error (-180 to +180)
        angle_diff = (desired_angle_deg - r_heading + 180) % 360 - 180
        self.heading_error_deg = round(angle_diff, 1)

        # STATE TRANSITIONS
        if state == "NAVIGATING_TO_PRE_ENTRY":
            if dist_cm <= self.target_reached_threshold_cm + 5.0:
                logger.info(f"Rover reached 20cm pre-entry waypoint for {mission}! Transitioning to slow direct entry.")
                with self.lock:
                    self.state = "NAVIGATING_TO_ENTRY"
                    self.status_message = f"Aligned at 20cm front. Slowly entering {mission} Entry Point."
                self._send_rover_cmd("stop")
                time.sleep(0.3)
                return
            else:
                # Steer rover towards pre-entry waypoint
                self._visual_servo_step(angle_diff, dist_cm, speed=160)

        elif state == "NAVIGATING_TO_ENTRY":
            if dist_cm <= self.target_reached_threshold_cm:
                logger.info(f"Rover ARRIVED at {mission} Entry! Tag locked and verified. Engaging AUTO patrol mode.")
                with self.lock:
                    self.state = "AUTO_PATROLLING"
                    self.status_message = f"ARRIVED at {mission}! Switched to Firmware AUTO Patrol Mode."
                # 1. Stop steering
                self._send_rover_cmd("stop")
                time.sleep(0.5)
                # 2. Trigger firmware auto patrol mode
                self._send_rover_cmd("auto_on")
                return
            else:
                # Slow crawl into entry
                self._visual_servo_step(angle_diff, dist_cm, speed=120)

        elif state == "NAVIGATING_TO_DOCK":
            if dist_cm <= self.target_reached_threshold_cm:
                logger.info("Rover successfully arrived at Charging Station / Dock (Tag 1)! Locked in dock position.")
                with self.lock:
                    self.state = "DOCKED"
                    self.status_message = "DOCKED: Rover safely parked at Charging Station (Tag 1)."
                self._send_rover_cmd("stop")
                return
            else:
                self._visual_servo_step(angle_diff, dist_cm, speed=140)

    def _visual_servo_step(self, heading_error_deg: float, dist_cm: float, speed: int = 150):
        """Sends closed-loop steering pulses to Rover based on heading error."""
        self._send_rover_speed(speed)

        # 1. If heading error is large, rotate in place
        if heading_error_deg > self.angle_tolerance_deg:
            self._send_rover_cmd("right")
        elif heading_error_deg < -self.angle_tolerance_deg:
            self._send_rover_cmd("left")
        else:
            # 2. Heading is aligned, drive forward
            self._send_rover_cmd("forward")

    def _annotate_frame(self, frame: np.ndarray, detected: Dict[int, Any]) -> np.ndarray:
        """Draws bounding boxes, labels, vectors, and status HUD over base camera feed."""
        h, w = frame.shape[:2]

        # Draw Base boundary & Grid
        cv2.rectangle(frame, (30, 30), (w - 30, h - 30), (70, 70, 80), 1)

        # Draw static and detected AprilTags
        for tag_id, name in TAG_NAMES.items():
            pos = self.tag_positions.get(tag_id)
            if pos:
                tx, ty = int(pos["x"]), int(pos["y"])
                locked = pos.get("locked", False)
                color = (0, 255, 120) if locked else (0, 200, 255)
                
                # Tag box
                cv2.circle(frame, (tx, ty), 10, color, -1)
                cv2.circle(frame, (tx, ty), 14, (255, 255, 255), 1)
                
                label = f"ID {tag_id}: {name}" + (" [LOCKED]" if locked else "")
                cv2.putText(frame, label, (tx + 12, ty + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Draw Rover position & heading arrow
        rx, ry = int(self.rover_pose["x"]), int(self.rover_pose["y"])
        if rx > 0 and ry > 0:
            angle_rad = math.radians(self.rover_pose["heading_deg"])
            arrow_x = int(rx + 35 * math.cos(angle_rad))
            arrow_y = int(ry + 35 * math.sin(angle_rad))
            
            # Rover circle & heading vector
            cv2.circle(frame, (rx, ry), 16, (0, 100, 255), -1)
            cv2.circle(frame, (rx, ry), 20, (255, 255, 255), 2)
            cv2.arrowedLine(frame, (rx, ry), (arrow_x, arrow_y), (0, 255, 255), 3, tipLength=0.3)
            cv2.putText(frame, "ROVER (Tag 0)", (rx - 35, ry - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)

        # HUD Overlay Banner
        cv2.rectangle(frame, (0, 0), (w, 36), (20, 24, 33), -1)
        hud_text = f"STATE: {self.state} | DIST: {self.distance_to_target_cm}cm | ERR: {self.heading_error_deg} deg"
        cv2.putText(frame, hud_text, (15, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 200), 1)

        return frame

    def get_status(self) -> Dict[str, Any]:
        """Returns full real-time telemetry of the AprilTag guidance engine."""
        return {
            "state": self.state,
            "mission_target": self.mission_target,
            "status_message": self.status_message,
            "rover_pose": self.rover_pose,
            "distance_to_target_cm": self.distance_to_target_cm,
            "heading_error_deg": self.heading_error_deg,
            "tag_positions": self.tag_positions,
            "camera_online": self.last_frame is not None,
            "rover_ip": self.rover_ip
        }

# Global singleton instance
guidance_controller = AprilTagGuidanceController(rover_ip=os.getenv("ROVER_IP", "10.208.70.197"))
