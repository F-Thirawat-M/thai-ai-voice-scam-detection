# Pilot-only code

- `pilot_data.py`: strict loader ของ `pilot_v1` เท่านั้น และ fixed-window Dataset
- `overfit.py`: เลือก paired Train subset และ bounded memorization diagnostic
- `batchnorm.py`: ตั้งโหมด BN โดยไม่ปิด dropout/ไม่ freeze affine parameters และตรวจ running buffers สำหรับคู่เปรียบเทียบ
- `learning_curve.py`: Frozen BN epoch/evaluation/Dev checkpoint selection/กราฟ สำหรับ pilot ที่จำกัด 3 epochs ไม่ใช่ main-run trainer
- `seed_stability.py`: ตรวจ/สรุปสาม seeds บน split เดิม ยอมรับเพียง seed CLI extension และ checkout newlines เมื่อรวมผลเก่า ไม่เลือก best seed

ไม่ใช่ generic research Dataset หรือ main trainer โค้ดที่ใช้ร่วมกันจริงอยู่ `../cvtts/` ส่วน network/inference อยู่ `../aasist/` และ `../rawnet2/`

ไม่ต้องเรียก functions เอง เปิด [Pilot README](../../../experiments/pilot/README.md) เพื่อเลือก notebook/script ตามขั้น
