# RESEARCH — แผนการทดลองจริง (ยังไม่เริ่ม)

**โฟลเดอร์นี้ยังไม่มี trainer/notebook ที่รัน main experiment ได้** ไม่ใช่ผลทดลอง ไม่ย้ายผล pilot มาเรียกว่างานจริง

เป้าหมายงานหลัก: Common Voice Thai + TTS หลายระบบ เปรียบเทียบ AASIST/RawNet2 และ Clean/Mixed ตาม protocol ที่ตกลงกับอาจารย์

ก่อนเริ่มต้องทำ:

1. ตรวจ recipe จาก pilot และล็อก scope/สิทธิ์/งบ/model/generators
2. สร้าง cohort/version และ Train/Dev/Final Test ของงานจริง แยกผู้พูด/ข้อความ/ไฟล์ซ้ำก่อนสร้าง TTS
3. ใช้ TTS อย่างน้อยสองระบบที่ผ่าน QC; กำหนด held-out generator ตาม scope ไม่เลือกจาก Test detector scores
4. เตรียม Noise/Telephone และตรึง Dev/Test conditions
5. เพิ่ม training/resume/selection และฝึกสี่แบบ: AASIST Clean/Mixed, RawNet2 Clean/Mixed อย่างเทียบกันได้
6. เลือก checkpoint/threshold จาก Dev แล้วประเมิน Final Test โดยไม่เอาผล Test กลับมาจูน
7. สรุป EER/ความผิดพลาด/compute/ข้อจำกัด

เมื่อ implement จริง ค่อยเพิ่ม `configs/`, `scripts/` ที่นี่ ไม่สร้างโค้ดเปล่าหรือไฟล์ mock ที่ทำให้เข้าใจว่ารันได้แล้ว ผลงานจริงจะแยก `results/research/<protocol>/<run_id>/` และ dataset version ใหม่ **เส้นทางนี้ยังเป็นข้อเสนอ ยังไม่มีข้อมูลดังกล่าว**

อ่าน [workflow วิจัยละเอียด](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md) โดยระวังคำสั่ง proposed ที่ยังไม่ได้ implement ถ้าจะทำงานตอนนี้ให้กลับไป [pilot/](../pilot/README.md)
