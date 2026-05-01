# 🎓 AI-Powered Online Exam Proctoring System

A real-time computer vision system that detects suspicious activities during online exams using webcam footage, audio monitoring, and screen recording.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 👤 Face Detection | Alerts when student's face is not visible |
| 👁️ Eye Tracking | Detects excessive eye movements (left/right/up/down) |
| 👀 Gaze Analysis | Monitors direction of eye gaze in real-time |
| 👄 Mouth Movement | Identifies potential talking or whispering |
| 👥 Multi-Face Alert | Detects when multiple faces appear in frame |
| 📱 Object Detection | Detects prohibited items (phone, book, etc.) |
| 🖥️ Screen Recording | Continuously captures examinee's screen activity |
| 🎙️ Audio Monitoring | Detects voice or whispering in the environment |
| 🔊 Voice Alerts | Real-time verbal warnings via text-to-speech |
| 📊 Dashboard | Live visual interface with detection metrics |
| 📄 Report Generation | PDF and HTML reports with heatmaps and timeline |

---

## 🛠️ Technologies Used

- **Python 3.8+**
- **OpenCV** — Computer vision processing
- **MediaPipe** — Face mesh and landmark detection
- **FaceNet-PyTorch / MTCNN** — Face detection
- **Flask** — Web dashboard
- **PyTorch** — Deep learning backend
- **Whisper** — Audio transcription (optional)

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/Shweta-nasc/ExamProctoring.git
cd ExamProctoring
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements-local.txt
```

### 4. Download pre-trained models
```bash
python -c "from facenet_pytorch import MTCNN; MTCNN(keep_all=True)"
```

---

## ▶️ Usage

### Run everything together (recommended)
```bash
python run.py
```
This will automatically start the dashboard and monitoring engine together.

### Or run separately

**Terminal 1 — Dashboard:**
```bash
python src/dashboard/app.py
```

**Terminal 2 — Monitoring Engine:**
```bash
python src/main.py
```

Access the dashboard at: **http://localhost:5000**

---

## ⚙️ Configuration

Edit `config/config.yaml` to customize behavior:

```yaml
video:
  source: 0                    # 0 for default webcam
  resolution: [1280, 720]
  fps: 30

detection:
  face:
    detection_interval: 5      # frames
    min_confidence: 0.8
  eyes:
    gaze_threshold: 2          # seconds
    blink_threshold: 0.3
    gaze_sensitivity: 15
  mouth:
    movement_threshold: 3      # consecutive frames
  objects:
    min_confidence: 0.65
  audio_monitoring:
    enabled: true
    sample_rate: 16000
    whisper_enabled: false
    whisper_model: "tiny.en"

logging:
  alert_cooldown: 10           # seconds between same alert
  alert_system:
    voice_alerts: true
    alert_volume: 0.8
```

---

## 🗂️ Project Structure
ExamProctoring/
├── config/              # Configuration files
├── models/              # Pretrained models
├── src/
│   ├── detection/       # Detection modules
│   ├── reporting/       # Report generation
│   ├── utils/           # Utility functions
│   ├── dashboard/       # Flask web dashboard
│   └── main.py          # Main application entry
├── logs/                # Session logs
├── recordings/          # Recorded sessions
├── run.py               # Single entry point launcher
└── requirements-local.txt
---

## 🔧 Troubleshooting

**Eye detection not accurate?**
- Ensure good lighting on your face
- Remove glasses if they cause glare
- Position camera at face level

**pyaudio install fails on Mac?**
```bash
brew install portaudio
pip install pyaudio
```

**Port 5000 already in use?**
```bash
lsof -ti:5000 | xargs kill -9
python run.py
```

**Models not downloading?**
- Check internet connection
- Run: `python -c "from facenet_pytorch import MTCNN; MTCNN(keep_all=True)"`

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## ☕ Support the Project

If you found this helpful, consider buying a coffee!

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/aarambhdevhub)

---

*Built with ❤️ for fair and secure online examinations.*