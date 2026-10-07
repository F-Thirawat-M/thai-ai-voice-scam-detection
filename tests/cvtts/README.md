# Tests สำหรับ pipeline ใหม่

มี tests ที่รันได้สำหรับ MMS text validation (`test_text.py`), shared canonical audio (`test_canonical_audio.py`) และ immutable artifact writes (`test_artifacts.py`) ทดสอบ stereo mean, resample/duration, amplitude preservation, finite/nonempty/nonzero, reproducible FLOAT WAV roundtrip และ conflict ก่อนสร้างไฟล์ใหม่ ไม่มีการใช้ dataset จริงเป็น test fixture

เพิ่ม `test_windows.py` / `test_pilot_data.py` ตรวจ crop แบบรวมจุดท้าย, ความยาวเท่ากันไม่เรียก random range ว่าง, repeat, silent window, seeded reproducibility, label order, manifest/audio/source hashes และ split overlap ด้วย fixture ที่สร้างเอง ไม่มีการโหลด GPU/model จริงใน unit tests ส่วน gradient/parameter-change/checkpoint reload ตรวจใน script smoke บนเครื่องที่มี upstream/weights/data ดู [คู่มือ](../../docs/AASIST_CLEAN_SMOKE_TH.md)

สร้าง unit/integration tests เพิ่มตาม [workflow ส่วน 18](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s18) เมื่อเริ่ม implementation ส่วนอื่น tests เหล่านี้ไม่ได้ยืนยันว่าคำอ่านทั้งหมดถูกหรือ model generalize ได้

`test_overfit.py` ตรวจ paired Train selection, finite/label validation, gradient learning ขณะ dropout/BN stats ตรึง, accumulation รวม microbatch ที่ขนาดไม่เท่ากัน และ checkpoint reload ด้วยโมเดลจำลอง; `test_overfit_guard.py` ตรวจ Train-only entry point/ไม่ทับ run/งบจำกัด; `test_provenance.py` ตรวจ exact/LF-CRLF และปฏิเสธ code changes จริง ผล AASIST จริงแยกอยู่ใน [คู่มือ overfit check](../../docs/AASIST_OVERFIT_CHECK_TH.md)

ใช้ fixtures ที่สร้างเองและแจกได้ ทดสอบ split isolation, shared audio/conditions, generation resume, gradients/save-load และ Dev-only threshold ก่อนเปิด Final Test

Tests ระดับ baseline ที่ยังใช้อยู่คือ `../test_audio.py` และ `../test_metrics.py`; ผ่านสองไฟล์นี้ไม่ได้แปลว่า protocol ใหม่ผ่านแล้ว
