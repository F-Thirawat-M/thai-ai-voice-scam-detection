# Tests สำหรับ pipeline ใหม่

สร้าง unit/integration tests ตาม [workflow ส่วน 18](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s18) เมื่อเพิ่ม implementation ขณะนี้ไม่มี CV/TTS tests ที่รันได้ในโฟลเดอร์นี้

ใช้ fixtures ที่สร้างเองและแจกได้ ทดสอบ split isolation, shared audio/conditions, generation resume, gradients/save-load และ Dev-only threshold ก่อนเปิด Final Test

Tests ระดับ baseline ที่ยังใช้อยู่คือ `../test_audio.py` และ `../test_metrics.py`; ผ่านสองไฟล์นี้ไม่ได้แปลว่า protocol ใหม่ผ่านแล้ว
