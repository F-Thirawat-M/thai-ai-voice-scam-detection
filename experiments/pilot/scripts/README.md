# Pilot scripts — ไม่ใช่การทดลองวิจัยจริง

- `train_aasist_clean.py`: Clean 1 epoch / short preflight ใช้ Train 160 และ Dev 40
- `check_aasist_overfit.py`: ฝึกซ้ำ Train 4 คลิปแบบคงที่ ไม่โหลด Dev/Test

รันจาก project root ไม่จำเป็นต้อง cd เข้ามา ใช้ `.venv` หลัก ผลอยู่ `results/pilot/` แต่ละ run ต้องชื่อใหม่ ไม่ overwrite ผลเดิม

ดูคำสั่ง/ผลที่ [Pilot README](../README.md) ยังไม่มี RawNet2 trainer หรือ main-run trainer ที่นี่
