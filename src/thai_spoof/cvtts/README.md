# Shared Common Voice / TTS pipeline

มี helper `text.py` สำหรับเตรียมตัว “ำ” ของ MMS Thai pilot เป็นอักษรที่ tokenizer รองรับ และหยุดเมื่อ tokenizer เปลี่ยน/ตัดข้อความหลังเตรียมโดยไม่ประกาศ พร้อม tests ที่ `tests/cvtts/test_text.py`

เพิ่ม `audio.py` สำหรับ downmix ค่าเฉลี่ยและ resample เสียงเต็มคลิปเป็น mono 16 kHz แล้ว encode WAV FLOAT โดยไม่ normalize gain/clip/trim/crop/pad มี source measurements และตรวจ float32 roundtrip นี่เป็น **shared canonical preparation** ไม่ใช่ fixed-window input ของ model ไม่เรียก helper inference ที่ปรับ peak เกิน 1 อัตโนมัติ และยังไม่เลือก training-window policy

`artifacts.py` ตรวจ conflict ทุกไฟล์ก่อนสร้าง derived artifacts ด้วย exclusive writes ไม่เขียนทับหรือทำ backup ใช้ใน [notebook เตรียมเสียง pilot](../../../data/exploration/common_voice/common_voice_pilot_audio.ipynb) รูปแบบเหมือนกันทั้งสองคลาสไม่ได้ลบ artefacts/ข้อจำกัดแบนด์วิดท์จากต้นทาง

ยังไม่มี training DataLoader, TTS adapter, augmentation, trainer หรือคำสั่ง pipeline ฝึกใหม่ ตัวอย่างสร้างเสียงและชุด pilot อยู่ใน notebooks ไม่ใช่ pipeline วิจัยเต็ม

งานที่จะพัฒนาตาม [workflow](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md): audit/split/schemas/provenance → synthesis → shared audio/conditions/datasets → training adapters → scoring/evaluation/reporting

คง model-specific network/inference code ใน `../aasist/` และ `../rawnet2/` ส่วน data split/augmentation/score convention ใช้ร่วมกันที่นี่ ไม่คัดลอก pipeline ให้โมเดลละชุด

ให้สร้าง modules เมื่อเริ่ม task ที่เกี่ยวข้องพร้อม tests ไม่สร้าง implementation เปล่าที่คืนค่าหลอกว่างานสำเร็จ
