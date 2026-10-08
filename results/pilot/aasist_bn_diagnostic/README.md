# ผลเปรียบเทียบโหมด BatchNorm ใน AASIST pilot

ข้อมูลจริง/logs/weights/comparison JSON ไม่อยู่ใน Git มีเพียง README นี้

- `<pair_id>/`: สถานะคู่ใน `run.json` และผลตรวจ/เปรียบเทียบใน `comparison.json`
- `<pair_id>_train/`: Train 160 / Dev 40, BatchNorm โหมด train ปกติ
- `<pair_id>_frozen/`: ข้อมูล/recipe เดียวกัน แต่ BatchNorm ใช้ running statistics เดิม; dropout ยังเปิด และ affine parameters ยังเรียนรู้

ทั้งสองเริ่มจาก pretrained เดิม ฝึกแค่ 1 epoch/seed ไม่ใช่ Final Test หรือการเลือกสูตรที่ดีที่สุด ใช้ชื่อคู่ใหม่ทุกครั้ง ดู [คู่มือ](../../../experiments/pilot/docs/aasist/AASIST_BATCHNORM_CHECK_TH.md)
