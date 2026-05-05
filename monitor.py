"""
Sit Still Monitor
=================
Uses your webcam to detect excessive movement and reminds you to sit still.
Active only between 9:00 AM and 5:00 PM. Press 'q' or Ctrl+C to stop.
"""

import cv2
import time
import datetime
import sys
import signal
import threading
import numpy as np

# ─── CONFIGURATION ──────────────────────────────────────────────
WORK_START_HOUR = 9        # 9 AM
WORK_END_HOUR = 17         # 5 PM
MOTION_THRESHOLD = 30      # Pixel intensity change threshold (0-255)
MOTION_AREA_PCT = 3.0      # % of frame that must change to trigger alert
CHECK_INTERVAL = 0.5       # Seconds between frame checks
COOLDOWN_SECONDS = 10      # Min seconds between consecutive alerts
CAMERA_INDEX = 0           # 0 = default webcam
SHOW_PREVIEW = True        # Set False to run headless (no camera window)
# ────────────────────────────────────────────────────────────────

# Global flag for graceful shutdown
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running
    print("\n🛑 Stopping monitor... Goodbye!")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def is_work_hours() -> bool:
    """Check if current time is within the 9-to-5 work window."""
    now = datetime.datetime.now()
    return WORK_START_HOUR <= now.hour < WORK_END_HOUR


def alert_sit_still():
    """Send a 'sit still' alert — speaks out loud."""
    timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
    print(f"⚠️  [{timestamp}] Too much movement detected — SIT STILL! 🪑")

    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("You are not still")
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"🔇 Could not speak: {e}")
        print("\a", end="", flush=True)  # Fallback to terminal bell


def compute_motion(prev_gray, curr_gray) -> float:
    """
    Compute the percentage of pixels that changed significantly
    between two grayscale frames.
    """
    frame_diff = cv2.absdiff(prev_gray, curr_gray)
    _, thresh = cv2.threshold(frame_diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)

    # Reduce noise with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    motion_pixels = cv2.countNonZero(thresh)
    total_pixels = thresh.shape[0] * thresh.shape[1]
    motion_pct = (motion_pixels / total_pixels) * 100

    return motion_pct


def main():
    global running

    print("=" * 55)
    print("  🎥  SIT STILL MONITOR  ")
    print("=" * 55)
    print(f"  ⏰  Active hours : {WORK_START_HOUR}:00 AM – {WORK_END_HOUR - 12}:00 PM")
    print(f"  📷  Camera index : {CAMERA_INDEX}")
    print(f"  🎯  Sensitivity  : {MOTION_AREA_PCT}% motion area")
    print(f"  🔇  Cooldown     : {COOLDOWN_SECONDS}s between alerts")
    print(f"  🖥️   Preview      : {'ON' if SHOW_PREVIEW else 'OFF'}")
    print("-" * 55)
    print("  Press 'q' in the camera window or Ctrl+C to stop.")
    print("=" * 55)

    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ ERROR: Could not open camera. Check your webcam connection.")
        sys.exit(1)

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        print("❌ ERROR: Could not read from camera.")
        cap.release()
        sys.exit(1)

    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
    last_alert_time = 0

    print(f"\n✅ Monitor started at {datetime.datetime.now().strftime('%I:%M %p')}\n")

    while running:
        # ── Check work hours ──
        if not is_work_hours():
            now = datetime.datetime.now()
            print(f"\r💤 Outside work hours ({now.strftime('%I:%M %p')}). "
                  f"Waiting for {WORK_START_HOUR}:00 AM...", end="", flush=True)
            time.sleep(30)  # Check every 30 seconds when outside hours
            continue

        # ── Capture frame ──
        ret, frame = cap.read()
        if not ret:
            print("⚠️  Frame capture failed. Retrying...")
            time.sleep(1)
            continue

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.GaussianBlur(curr_gray, (21, 21), 0)

        # ── Detect motion ──
        motion_pct = compute_motion(prev_gray, curr_gray)

        # ── Alert if too much movement ──
        current_time = time.time()
        if motion_pct > MOTION_AREA_PCT:
            if (current_time - last_alert_time) > COOLDOWN_SECONDS:
                alert_sit_still()
                last_alert_time = current_time

        # ── Show preview window (optional) ──
        if SHOW_PREVIEW:
            # Draw status overlay
            status = "MOVING!" if motion_pct > MOTION_AREA_PCT else "Still"
            color = (0, 0, 255) if motion_pct > MOTION_AREA_PCT else (0, 255, 0)
            cv2.putText(frame, f"Motion: {motion_pct:.1f}% | {status}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, "Press 'q' to quit",
                        (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (200, 200, 200), 1)
            cv2.imshow("Sit Still Monitor", frame)

            # Check for 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n🛑 'q' pressed — stopping monitor.")
                break

        prev_gray = curr_gray
        time.sleep(CHECK_INTERVAL)

    # ── Cleanup ──
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Monitor stopped. Have a great day! 👋")


if __name__ == "__main__":
    main()