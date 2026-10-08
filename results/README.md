# ผลทดลองในเครื่อง (ไม่อยู่ใน Git)

Git เก็บคู่มือ/ไฟล์ว่างแสดงโฟลเดอร์เท่านั้น ไม่เก็บ logs/scores/checkpoints/ZIP

- `pilot/aasist_clean_smoke/`: ผล AASIST Clean Train 160 / Dev 40
- `pilot/aasist_overfit_check/`: ผล AASIST จำ Train 4 คลิป
- `pilot/aasist_bn_diagnostic/`: เปรียบเทียบสองรอบ เปลี่ยนเฉพาะโหมด BatchNorm
- `pilot/rawnet2/`: พื้นที่เพื่อนสำหรับผล RawNet2 ยังไม่มี run
- `pilot/share/`: ZIP สำหรับส่งข้อมูลในทีม ไม่ใช่ผลโมเดล

ผลจริงมี `<run_id>/` ต้องใช้ชื่อใหม่ทุกครั้ง ไม่ลบ/ทับผลเดิม ยังไม่มี results ของงานวิจัยหลัก ดู [คู่มือ pilot](../experiments/pilot/README.md)
