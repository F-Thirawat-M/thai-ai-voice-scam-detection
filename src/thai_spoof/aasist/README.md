# AASIST — ฝั่ง F-Thirawat-M

โฟลเดอร์นี้รวมตัวเชื่อมโมเดล (`detector.py`), การเตรียมเสียง (`audio.py`)
และค่าตั้งต้น (`config.json`) จากฝั่ง repo ของ F-Thirawat-M

โครงสร้างเครือข่าย AASIST มาจาก `external/aasist/` ซึ่งดาวน์โหลดจาก
https://github.com/clovaai/aasist ด้วย `scripts/setup.ps1`
น้ำหนักที่ใช้รันอยู่ที่ `checkpoints/aasist/AASIST.pth`

รันจากโฟลเดอร์หลัก:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model aasist --audio data\sample\your_voice.wav
```
