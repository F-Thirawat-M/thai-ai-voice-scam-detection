# ตัวอย่างที่แจกได้

`inference_manifest.csv` แสดง schema ขั้นต่ำของ CLI เดิม: `path,label` มีชื่อไฟล์สมมติสองชื่อ ไม่ใช่ corpus หรือผลทดลอง

สร้างไฟล์ manifest จริงใน `data/processed/cvtts/<version>/manifests/` โดยเปลี่ยน path และ label ตามข้อมูลของตนเอง ก่อนใช้ `evaluate` ต้องมีทั้งสอง label หากต้องการคำนวณ metrics

อย่าเอาเสียงจริง metadata ผู้พูด หรือ token มาใส่โฟลเดอร์นี้ เพราะไฟล์ที่นี่เข้า Git ได้ ดู [ข้อจำกัดของ CLI เดิม](../README.md#ประเมินหลายไฟล์ด้วย-cli-เดิม)
