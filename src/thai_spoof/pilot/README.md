# Pilot-only code

- `pilot_data.py`: strict loader ของ `pilot_v1` เท่านั้น และ fixed-window Dataset
- `overfit.py`: เลือก paired Train subset และ bounded memorization diagnostic

ไม่ใช่ generic research Dataset หรือ main trainer โค้ดที่ใช้ร่วมกันจริงอยู่ `../cvtts/` ส่วน network/inference อยู่ `../aasist/` และ `../rawnet2/`

ไม่ต้องเรียก functions เอง เปิด [Pilot README](../../../experiments/pilot/README.md) เพื่อเลือก notebook/script ตามขั้น
