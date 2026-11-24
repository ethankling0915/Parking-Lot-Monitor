# parking-lot-monitor

Watches a parking lot through a USB webcam with YOLO, logs when a parking zone becomes occupied or vacant, and runs as a daytime service on a Jetson Orin Nano.

Developed and tested on Windows (NVIDIA RTX 3070), deployed to the Jetson.

**Status:** milestone 1 scaffold. Not yet run end to end on either machine.

## Layout

- `parking_monitor/` - the application
- `config/config.example.yaml` - copy to `config/config.yaml` and edit (the real file is git-ignored)
- `scripts/record_clip.py` - record test clips from the webcam
- `scripts/export_tensorrt.py` - build a TensorRT engine (Jetson only)
- `deploy/parking-monitor.service` - systemd unit (Jetson only)
- `tests/` - unit tests for zone and occupancy logic

## Develop on Windows

PowerShell, from the repo folder:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
# Install a CUDA build of PyTorch that matches your driver. Get the command from pytorch.org.
pip install -r requirements.txt
copy config\config.example.yaml config\config.yaml
python scripts\record_clip.py 0 10
python -m parking_monitor.main --source clips\<clip-name>.mp4 --db data\test.db --ignore-window --show
pytest
```

Notes:
- Camera index `0` is the first camera Windows sees. If you have a laptop webcam, the Brio may be `1`.
- Use `--db data\test.db` for clip tests so replay events don't mix with live events.
- The zone polygons in the example config are placeholders. Pick real coordinates from a frame of your clip. Most paint programs show pixel coordinates.

## Deploy to the Jetson

1. Clone the repo on the Jetson.
2. Use JetPack's OpenCV and NVIDIA's PyTorch build for the Jetson. Don't install the generic PyTorch wheel from PyPI, because it won't use the GPU. Ultralytics' Jetson guide has the current steps.
3. Create the venv with system packages visible so JetPack's OpenCV and PyTorch are available:
   ```bash
   python3 -m venv --system-site-packages .venv
   .venv/bin/pip install -r requirements-jetson.txt
   ```
   `ultralytics` can pull in a generic `opencv-python` that replaces JetPack's build. If that happens, reinstall the JetPack build.
4. Copy `config/config.example.yaml` to `config/config.yaml`. Set `source` to the Brio's device index (usually `0`) and `model` to the engine file.
5. Build the engine on the Jetson:
   ```bash
   .venv/bin/python scripts/export_tensorrt.py yolo26n.pt 960
   ```
   Set `model` and `imgsz` in the config to match. TensorRT engines only run on the device that built them, so never copy them between machines.
6. Install the service. Edit `User` and the paths in `deploy/parking-monitor.service`, then:
   ```bash
   sudo cp deploy/parking-monitor.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now parking-monitor
   ```

### Pausing when you need the Jetson or the camera

- `touch data/PAUSE` pauses the monitor and releases the camera. `rm data/PAUSE` resumes it.
- `sudo systemctl stop parking-monitor` stops it until you start it again.

## Roadmap

1. Zone occupancy from the webcam, with debounced events in SQLite (this scaffold)
2. Recognize your own car and count visits
3. Daily summary page
4. Optional on-demand LLM questions over the event database
