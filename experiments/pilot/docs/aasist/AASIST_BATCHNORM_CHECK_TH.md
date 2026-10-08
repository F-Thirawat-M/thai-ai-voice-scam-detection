# AASIST pilot — ตรวจผลของโหมด BatchNorm ทีละปัจจัย

## ทำอะไรและทำไม

Clean smoke เดิมฝึก/reload ได้ แต่ Dev loss เพิ่ม 1.594355 → 4.853433 การจำ Train 4 คลิปที่ผ่านแสดงว่าโมเดลเรียนรู้ได้ ไม่ได้ตอบว่าทำไม Dev แย่ลง จึงทดลองปัจจัยเดียวก่อน: **โหมด BatchNorm ระหว่างฝึกด้วย microbatch 2**

BatchNorm เป็นส่วนปรับสเกล activations ในโครงข่าย AASIST ในโหมด train ใช้สถิติของ batch ที่กำลังผ่าน และอัปเดต running mean/variance สำหรับ inference การรวม gradient 8 microbatches ไม่ได้รวมสถิติ BN ให้กลายเป็น batch 16

เทียบสองรอบใหม่อย่างละ 1 epoch จาก pretrained เดียวกัน ไม่เอา checkpoint ที่จำ 4 คลิปหรือ smoke เก่ามาฝึกต่อ:

| ปัจจัย | Train BN | Frozen BN |
| --- | --- | --- |
| การ normalize โดย BN ตอน Train | ใช้สถิติ batch ปัจจุบัน | ใช้ running statistics จาก pretrained |
| Running mean/variance/counts | อัปเดตระหว่าง Train | ไม่เปลี่ยน |
| BN affine weights/bias | เรียนรู้ | เรียนรู้ |
| Dropout | เปิดระหว่าง Train | เปิดระหว่าง Train |
| Seed/data/window/ลำดับคลิป/optimizer | เหมือนกัน | เหมือนกัน |

**Frozen BN ไม่ได้แค่หยุด EMA** แต่เปลี่ยนสถิติที่ใช้ normalize ตอน Train ด้วย ไม่ freeze น้ำหนักทั้งโมเดล และไม่ใช้ `model.eval()` ทั้งโมเดลระหว่างฝึกเหมือน diagnostic จำ 4 คลิป

## สิ่งที่คงเดิม

- Train 160 (คน 80 / Wayu 80), Dev 40 (คน 20 / Wayu 20) ไม่มี Test loader
- WAV mono 16 kHz เต็มคลิป; model window 64,600 samples, crop Train แบบ seeded ครั้งเดียว, Dev ช่วงแรก, คลิปสั้น repeat
- Seed 42, microbatch 2 × accumulation 8 = effective batch 16, 80 microbatches / 10 updates ต่อ arm
- AdamW LR `1e-5`, weight decay `1e-4`, clip norm 1, CE ไม่ถ่วง class, float32 ไม่มี AMP
- ไม่มี Noise/Telephone/frequency masking/gain normalization ไม่มี scheduler/resume/best checkpoint
- ทุก parameter เรียนรู้ ไม่เขียนทับ pretrained/data/run เก่า

## รันอย่างไร

ใช้ [check_aasist_batchnorm.py](../../scripts/aasist/check_aasist_batchnorm.py) จาก project root ด้วย `.venv` หลัก ต้องมี dataset/upstream/weights เดิม ถ้ารันไว้แล้วไม่ต้องรันซ้ำ ใช้ชื่อคู่ใหม่เมื่อจะทดลองใหม่:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\check_aasist_batchnorm.py --run-id bn_my_pair_01 --device cuda
```

Driver เรียก `train_aasist_clean.py --diagnostic-bn train` และ `--diagnostic-bn frozen` ใน subprocess แยกกัน เพื่อ reset RNG/model เริ่มต้นอย่างอิสระ ใช้ namespace `results/pilot/aasist_bn_diagnostic/` ส่วนคำสั่ง smoke เดิมที่ไม่ใส่ flag ยังอยู่ `aasist_clean_smoke/`

Driver ตรวจชื่อคู่/ทั้งสอง arm ว่ายังไม่มี หากรอบใดล้มเหลวจะเก็บสถานะ failed และไฟล์ที่ได้ถึงตอนนั้น ไม่ทับ/ลบเพื่อรันใหม่ และไม่รายงานว่าได้ comparison สำเร็จ

## ตรวจความเทียบกันได้อย่างไร

- Hash ของ dataset/report/weights/upstream/source code เท่ากันทั้งคู่
- Recipe ต่างเพียง `batchnorm_mode`; environment และจำนวน Train/Dev/updates ตรงกัน
- Train sample order/crop ตรงกันทุกคลิป และ logits Dev ก่อนฝึกตรงกันภายใน tolerance
- BN buffers เปลี่ยนจริงใน Train arm แต่ไม่เปลี่ยนใน Frozen arm
- สถานะ completed, parameters เปลี่ยน, gradients/weights finite, fresh-model reload ผ่าน
- ตรวจ hashes ของ logs/scores/checkpoints ก่อนสร้าง comparison

## เปิดอะไรดูผล

`results/pilot/aasist_bn_diagnostic/<pair_id>/comparison.json` มี Dev loss ก่อนฝึก/หลังฝึกทั้งสอง arm และ `frozen_minus_train_dev_loss` (ค่าติดลบหมายถึง Frozen ต่ำกว่า Train ในรอบนี้)

แต่ละ `<pair_id>_train/`, `<pair_id>_frozen/` มี `run.json`, `training_log.json`, `dev_scores.csv`, `last.pt` เช่น smoke เดิม ไม่ขึ้น Git ดู `batchnorm_audit` สำหรับ counters และ buffers ที่เปลี่ยน

## ผลคู่แรก 8 ตุลาคม 2026

Pair ID: `bn_pair_20261008_v1` บน RTX 3050 Ti Laptop GPU ตรวจคู่ผ่านแล้ว:

| รอบ | Dev cross-entropy loss (ต่ำกว่าดีกว่า) |
| --- | --- |
| Pretrained ก่อนฝึก ทั้งสอง arm | 1.594355 |
| หลังฝึก 1 epoch — Train BN | 4.853433 |
| หลังฝึก 1 epoch — Frozen BN | 1.074124 |

Frozen ต่ำกว่า Train BN 3.779310 และต่ำกว่า pretrained ในคู่นี้ ตรวจ dataset/recipe/source hashes, Train order/crops และ logits เริ่มต้นตรงกัน ผล Train BN ทำซ้ำได้เท่ารอบ smoke เดิม แต่ไม่ได้แก้/ทับผลเก่า

- มี BN 18 layers / 54 buffers: Train arm เปลี่ยน 54 buffers และ counters เพิ่ม layer ละ 80; Frozen arm ไม่เปลี่ยน buffer และ counters เพิ่ม 0
- Parameters เปลี่ยนจริง 155 tensors ใน Train arm และ 154 ใน Frozen arm (ทุก parameter เปิดให้เรียนรู้ การเปลี่ยนทุก tensor ไม่ใช่เกณฑ์บังคับ)
- ทั้งสองโหลด `last.pt` เข้าโมเดลใหม่แล้ว logits Dev ตรงกัน: max absolute error 0
- มี 10 optimizer updates ต่อ arm ไม่ใช่การจำ 4 คลิป; ไม่อ่าน Final Test ไม่รายงาน EER/accuracy

ผลนี้สนับสนุนให้ตรวจแนวทาง Frozen BN ต่อภายใน Train/Dev แต่ **ยังไม่ล็อกเป็น recipe งานวิจัยหลัก** และไม่แปลว่าพิสูจน์สาเหตุของ Dev loss เดิมครบทั้งหมด

## ตีความและขอบเขต

Dev cross-entropy ต่ำลงเป็นสัญญาณสำหรับพัฒนา recipe ไม่ใช่ Test accuracy/EER หาก Frozen ดีกว่า แปลว่าการเปลี่ยนโหมด BN ช่วยใน **คู่นี้** ไม่ได้พิสูจน์ว่า running statistics เป็นสาเหตุทั้งหมด หรือว่า Frozen ดีที่สุดเสมอ

นี่คือ seed เดียว/1 epoch/Wayu ระบบเดียวและข้อมูลเล็ก ต้องยืนยันด้วยงบ Train/Dev ที่กำหนดก่อนล็อก recipe ไม่ใช้ Final Test ไล่ปรับค่า และไม่อ้างความสำเร็จ Clean vs Mixed หรือ RawNet2 จากผลนี้
