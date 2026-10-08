# AASIST Frozen BN — ตรวจความแกว่งของ seeds 42 / 43 / 44

## เป้าหมายและงบ

Frozen BN seed 42 แบบ 3 epochs ลด Dev CE จาก 1.594355 เป็น 0.338209 จึงตรวจว่าผลลดลงสม่ำเสมอในเลขสุ่มอื่นด้วยหรือไม่ ก่อนขยายการทดลอง

กำหนดไว้ล่วงหน้าให้รายงาน **seeds 42, 43, 44 ทั้งหมด** ใช้ผล 42 เดิมที่ตรวจผ่าน ฝึกใหม่เฉพาะ 43/44 อย่างละ 3 epochs (เพิ่ม 6 epochs รวมทั้งสามเป็น 9 epochs / 90 updates) ไม่เพิ่ม seeds ไปเรื่อย ๆ ตาม Dev ไม่เลือกเฉพาะ seed ที่ดีที่สุด และไม่เพิ่ม Noise/Telephone/TTS/Test

Seed ควบคุมการสุ่มจุดเริ่ม Train crop, shuffle และ dropout ในรอบนั้น ทุก seed เริ่ม pretrained เดิม **ไม่ต่อจาก checkpoint epoch 3 ของรอบก่อน**

## อะไรเหมือน/ต่าง

เหมือน: Train 160 / Dev 40 เดิม, source/labels/split, pretrained, architecture, Frozen BN, dropout train, LR 1e-5, weight decay 1e-4, microbatch 2/accumulation 8, 3 epochs, loss/window policy และ checkpoint selection

ต่างโดยตั้งใจ: seed และผลการสุ่ม Train crops/order/dropout แต่ละ seed ใช้ crop ของตัวเองคงที่ตลอดสาม epochs ไม่มีการเปลี่ยนผู้พูด/ข้อความ/ไฟล์ใน cohort ส่วน **Dev clips/window/order ไม่เปลี่ยน**

Train evaluation loss ที่ epoch 0 อาจต่างกันเพราะใช้ Train crop คนละจุด ไม่ได้หมายความว่า initial weights เปลี่ยน ตัวตรวจเทียบ pretrained Dev logits ซึ่งใช้เสียง/ช่วงเดียวกันให้ตรงกันด้วย

## โค้ด/คำสั่ง

เพิ่ม `--seed` ใน [train_aasist_frozen_bn.py](../../scripts/aasist/train_aasist_frozen_bn.py) ค่า default ยังเป็น 42 ค่าอื่นของสูตรและงบ 3 epochs ไม่เปลี่ยน:

```powershell
# ตัวอย่างเมื่อจะฝึก single seed ใหม่: ใช้ run-id ใหม่เท่านั้น
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\train_aasist_frozen_bn.py --run-id frozen3_seed43_my01 --seed 43 --device cuda
```

คำสั่งสรุปทั้งสามใช้ [check_aasist_seed_stability.py](../../scripts/aasist/check_aasist_seed_stability.py):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\check_aasist_seed_stability.py --run-id seeds_my_suite01 --reference-run frozen3_20261008_v1 --device cuda
```

Driver ต้องมี reference seed 42 แบบ 3 epochs ที่ completed แล้ว ไม่อ่าน Test หรือสร้าง seed 42 ซ้ำให้อัตโนมัติ ถ้ารันชุดนี้แล้วไม่ต้องรันใหม่ ใช้ชื่อ suite ใหม่เมื่อทำรอบใหม่เท่านั้น หากชื่อ suite หรือ seed child มีอยู่ จะหยุดก่อนฝึก ไม่ทับ/ลบ/backup ผลเดิม

เครื่องเพื่อนที่ไม่มีผล seed 42 ต้องเตรียมรอบอ้างอิงเองด้วย code/data/environment เดียวกัน แล้วระบุชื่อผ่าน `--reference-run` การ pull Git ไม่ได้โหลด results/weights ให้ และยังไม่ใช่การฝึก RawNet2

## การตรวจเพื่อรวมผลเก่ากับใหม่

Helpers อยู่ `src/thai_spoof/pilot/seed_stability.py` ตรวจ completed/3 epochs/30 updates/480 exposures/Train 160/Dev 40, BN buffers, hashes ของ artifacts/checkpoints, checkpoint selection, Train clip set และ baseline Dev logits

Config ต้องต่างเพียง `seed`; dataset/pretrained/upstream/environment ต้องตรงกัน แหล่ง code ทุกไฟล์ต้องตรวจ hash ผ่าน ยอมรับ CRLF→LF จาก Git checkout เฉพาะ code ไม่ใช่เสียง/CSV

สำหรับ seed 42 ที่รันก่อนเพิ่ม flag ยอมรับความต่างเฉพาะสามจุดที่ตรวจย้อนด้วย source hash: เพิ่ม argument `--seed`, เพิ่ม range guard, เปลี่ยน `seed = 42` เป็น `seed = args.seed` พร้อม newline conversion เท่านั้น **ไม่แก้ report/source เก่าให้มี hash ใหม่** ถ้า source ต่างเกินนี้จะหยุด ไม่รวมผลแบบฝืนว่าควบคุมเหมือนกัน

ไม่มีการเปลี่ยนงบการฝึก, learning rate, epoch count หรือ window implementation เพื่อให้ผ่านการตรวจ compatibility

## อ่านผลที่ไหน/อย่างไร

Suite อยู่ `results/pilot/aasist_seed_stability/<suite_id>/`:

- `seed_curves.png`: เส้น Train evaluation และ Dev ของทุก seed พร้อมค่าเฉลี่ย (ไม่แสดงเฉพาะ winner)
- `summary.json`: ค่าทุก epoch/seed, ค่าเฉลี่ย, **sample standard deviation (`ddof=1`)**, min/max และผลตรวจ controls
- `run.json`: สถานะ/งบ/seeds/reference/driver hash/summary hash/plot hash

ผลโมเดล/weights ของ 43/44 อยู่ `results/pilot/aasist_frozen_bn_curve/<suite_id>_seed43/`, `<suite_id>_seed44/` เหมือนรอบ curve ก่อน

รายงานหลักของการตรวจนี้คือ Dev CE ณ **epoch 3 เดียวกันทุก seed** พร้อมค่าเฉลี่ยและ SD ส่วน checkpoint ที่ดีที่สุดภายใน epochs 1–3 เก็บแยกราย seed ตามกฎเดิม ไม่ใช้มันเลือก seed ที่ดีที่สุด

SD จากสาม seeds คือความแกว่งของการฝึกใน **split เดิม** ไม่ใช่ confidence interval, ไม่ใช่ความไม่แน่นอนจากการสุ่มผู้พูด/cohort และไม่รับประกัน performance กับเสียงใหม่/TTS อื่น ไม่มี Test accuracy/EER ในขั้นนี้

## ผลรัน 8 ตุลาคม 2026

Suite `seeds_20261008_v1` ตรวจ controls ผ่านแล้ว ใช้ reference 42 เดิมและรอบใหม่ 43/44 บนเครื่อง/GPU เดียวกัน:

| Seed | Train evaluation CE — epoch 3 | Dev CE — epoch 3 | Best epoch ภายใน 1–3 |
| --- | --- | --- | --- |
| 42 (ผลเดิม) | 0.530635 | 0.338209 | 3 |
| 43 | 0.557739 | 0.338875 | 3 |
| 44 | 0.618491 | 0.404151 | 3 |
| ค่าเฉลี่ยทั้งสาม | 0.568955 | 0.360412 | ไม่เลือก seed ที่ดีที่สุด |
| Sample SD (`ddof=1`) | 0.044989 | 0.037881 | ไม่ใช่ confidence interval |

Pretrained Dev CE เท่ากันทุก seed ที่ 1.594355 ทั้ง Train evaluation และ Dev CE ลดลงต่อเนื่องในสาม epochs ทุก seed ไม่เห็น Dev แย่ลงภายในงบนี้ แต่ไม่ได้แปลว่าไม่มี overfit หรือแม่นกับ Test

BN buffers คงเดิมในทุกรอบ ทุก checkpoint ของ 43/44 โหลดเข้าโมเดลใหม่ได้และ logits Dev ตรงกัน seed 42 ถูกอ่านอย่างเดียว ไม่เขียน report/hash/weights เดิมใหม่

ผลเพิ่มความเชื่อมั่นเฉพาะเรื่องการลด loss ใน pilot split นี้ ไม่ได้ยืนยัน main recipe, cross-generator robustness หรือความแม่นยำจริงของระบบ

กราฟ: `results/pilot/aasist_seed_stability/seeds_20261008_v1/seed_curves.png` สรุปตัวเลข/controls: `summary.json` ในโฟลเดอร์เดียวกัน ไม่ต้องรันซ้ำเพื่อเปิดดู

## ขอบเขตและงานถัดไป

นี่เป็นหลักฐานเรื่องความสม่ำเสมอของ pilot เพียงสาม seeds ใช้ Dev ในการพัฒนา recipe ไม่ใช่การยืนยันสูตรงานวิจัยหลักอย่างเด็ดขาด จากผลนี้ค่อยกำหนด protocol/cohort/generators/compute budget ก่อนขยายชุดข้อมูลและเปรียบเทียบ Clean/Mixed/AASIST/RawNet2 ไม่วนใช้ Test ปรับค่าฝึก
