# Shared Common Voice / TTS pipeline

มี helper `text.py` สำหรับเตรียมตัว “ำ” ของ MMS Thai pilot เป็นอักษรที่ tokenizer รองรับ และหยุดเมื่อ tokenizer เปลี่ยน/ตัดข้อความหลังเตรียมโดยไม่ประกาศ พร้อม tests ที่ `tests/cvtts/test_text.py` ยังไม่มี loader, TTS adapter, trainer หรือคำสั่ง pipeline ใหม่ ตัวอย่างสร้างเสียงอยู่ใน notebook ไม่ใช่ pipeline เต็ม

งานที่จะพัฒนาตาม [workflow](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md): audit/split/schemas/provenance → synthesis → shared audio/conditions/datasets → training adapters → scoring/evaluation/reporting

คง model-specific network/inference code ใน `../aasist/` และ `../rawnet2/` ส่วน data split/augmentation/score convention ใช้ร่วมกันที่นี่ ไม่คัดลอก pipeline ให้โมเดลละชุด

ให้สร้าง modules เมื่อเริ่ม task ที่เกี่ยวข้องพร้อม tests ไม่สร้าง implementation เปล่าที่คืนค่าหลอกว่างานสำเร็จ
