# sit-still-monitor
A Python-based webcam movement monitor that detects fidgeting and speaks "You are not still" to help you stay focused. Uses OpenCV for motion detection and pyttsx3 for voice alerts. Active only during work hours (9 AM – 5 PM).

# 🎥 Sit Still Monitor

A lightweight Python-based posture and movement monitoring tool that uses your webcam to detect excessive movement while you work. When it catches you fidgeting, it speaks out loud — *"You are not still"* — to remind you to stay focused.

## 🧠 Why I Built This

As someone who spends long hours at a desk, I wanted a simple, no-fuss way to keep myself aware of unnecessary movement and build better focus habits during work hours.

## ✨ Features

- **Real-time motion detection** using OpenCV frame differencing
- **Voice alerts** — your computer speaks to you instead of just beeping
- **9-to-5 scheduling** — only runs during work hours, sleeps otherwise
- **Live camera preview** with motion percentage overlay
- **Configurable sensitivity** — tune thresholds to your liking
- **Lightweight** — runs quietly in the background with minimal resources

## 🛠️ Tech Stack

- Python 3.9+
- OpenCV (computer vision & camera access)
- pyttsx3 (text-to-speech)
- NumPy

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/sit-still-monitor.git
cd sit-still-monitor
