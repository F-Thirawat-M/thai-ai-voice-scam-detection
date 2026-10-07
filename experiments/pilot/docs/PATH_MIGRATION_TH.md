# ย้ายตำแหน่ง ไม่ใช่รันการทดลองใหม่

Notebook/คำสั่ง/คู่มือย้ายมารวมใต้ `experiments/pilot/` ส่วนผลฝึกย้ายทั้งโฟลเดอร์ไป `results/pilot/` มีชื่อ run และเนื้อหาไฟล์เหมือนเดิม ไม่ทำ backup ซ้ำ

- Raw/Common Voice, `data/processed/cvtts/pilot_v1/` และ pretrained weights **ไม่ย้าย/ไม่แก้** เพื่อคง audio paths และ hashes ใน manifests
- ไฟล์ executed notebooks ย้ายมา `../notebooks/outputs/` โดยไม่แก้ผลลัพธ์/เนื้อหาที่รันแล้ว
- JSON/log/checkpoint เก่าไม่ถูกแก้ให้ใช้ code paths/hash ใหม่ สิ่งเหล่านี้บอก provenance ณ ตอนที่รันจริง ไม่ใช่ reference ที่ต้อง rewrite ทุกครั้ง
- หากตรวจ source hashes ของ run เก่า ให้ดู source จาก Git version ก่อน refactor; การเปลี่ยน ROOT/import/output paths ทำให้ hash code ปัจจุบันต่างได้ ไม่ได้แปลว่าข้อมูลเสียงถูกเปลี่ยน
- คำสั่งปัจจุบันใน scripts ใหม่บันทึก code paths และ output namespace ใหม่สำหรับ run ใหม่
- ยังคง ignore dataset, weights, results และ executed notebooks ไม่ใส่ข้อมูลเสียงขึ้น GitHub จากการจัดโครงสร้าง

แผนผัง old → new อยู่ใน [PROJECT_STRUCTURE_TH](../../../docs/PROJECT_STRUCTURE_TH.md) รายละเอียดการทดลองยังแยกเป็น [Clean smoke](AASIST_CLEAN_SMOKE_TH.md) และ [overfit check](AASIST_OVERFIT_CHECK_TH.md)
