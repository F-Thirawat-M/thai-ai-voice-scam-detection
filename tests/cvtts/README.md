# Tests สำหรับ pipeline ใหม่

มี tests ที่รันได้สำหรับ MMS text validation (`test_text.py`), shared canonical audio (`test_canonical_audio.py`) และ immutable artifact writes (`test_artifacts.py`) ทดสอบ stereo mean, resample/duration, amplitude preservation, finite/nonempty/nonzero, reproducible FLOAT WAV roundtrip และ conflict ก่อนสร้างไฟล์ใหม่ ไม่มีการใช้ dataset จริงเป็น test fixture

สร้าง unit/integration tests เพิ่มตาม [workflow ส่วน 18](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s18) เมื่อเริ่ม implementation ส่วนอื่น tests เหล่านี้ไม่ได้ยืนยันว่าคำอ่านทั้งหมดถูกหรือระบบฝึกสำเร็จ

ใช้ fixtures ที่สร้างเองและแจกได้ ทดสอบ split isolation, shared audio/conditions, generation resume, gradients/save-load และ Dev-only threshold ก่อนเปิด Final Test

Tests ระดับ baseline ที่ยังใช้อยู่คือ `../test_audio.py` และ `../test_metrics.py`; ผ่านสองไฟล์นี้ไม่ได้แปลว่า protocol ใหม่ผ่านแล้ว
