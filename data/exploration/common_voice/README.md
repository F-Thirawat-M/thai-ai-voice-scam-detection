# Common Voice EDA — ยังต้องพัฒนาใน T02

พื้นที่สำหรับ `common_voice_eda.ipynb` ตาม [workflow Phase 1](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s08) ยังไม่มี notebook หรือผลตรวจใหม่

งานแรก: ระบุ release/root/locale → อ่าน schema จริง → นับ missing/ผู้พูด/ข้อความ → ตรวจ path/decode/duration/sample rate/duplicate → รายงานเกณฑ์คัดและจำนวนคงเหลือ

ใช้ helper จาก `src/thai_spoof/cvtts/` ข้อมูลดิบอยู่ `data/raw/common_voice/<release>/` และผลเฉพาะเครื่องอยู่ `outputs/` ที่ไม่เข้า Git

ห้ามอนุมานว่า Common Voice ที่เพื่อนมีคือ release ล่าสุดจากจำนวนคลิป และห้ามรายงานจำนวนผู้พูดจริงจาก candidate ID โดยไม่อธิบายข้อจำกัด
