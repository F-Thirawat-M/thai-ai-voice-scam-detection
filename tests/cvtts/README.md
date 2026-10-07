# Tests ของ shared helpers

ทดสอบ audio preparation, windows, text, immutable writes และ provenance ด้วย fixture ที่สร้างเอง ไม่ใช้ dataset จริง

Tests เฉพาะ pilot Dataset / Clean script / overfit diagnostic อยู่ใน [../pilot/](../pilot/README.md) แล้ว การผ่าน tests ไม่รับประกันคุณภาพคำอ่านหรือ generalization ของ detector

รันทั้งหมดจาก root: `.\.venv\Scripts\python.exe -m pytest -q`
