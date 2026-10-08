# AASIST pilot — Frozen BatchNorm 3 epochs และกราฟ Train/Dev

## เป้าหมาย

หลังคู่ BN พบ Dev CE ปกติ 4.853433 / Frozen 1.074124 จาก pretrained 1.594355 จึงเพิ่มงบ Frozen BN เป็น **3 epochs ที่กำหนดก่อนรัน** ไม่เพิ่ม noise/generator หรือปรับ hyperparameters ไปพร้อมกัน ไม่ได้ล็อกสูตรงานวิจัยหลัก

Epoch คือผ่าน Train ทั้งชุดหนึ่งรอบ: 160 คลิป × 3 = **480 clip exposures แต่ยังเป็นคลิปไม่ซ้ำเดิม 160 คลิป** ไม่ใช่ได้ข้อมูลเพิ่ม 480 คลิป

## ค่าที่คงเดิม

- เริ่ม `checkpoints/aasist/AASIST.pth` ใหม่ ไม่ต่อจาก checkpoint ของ smoke/จำ 4 คลิป/คู่ BN
- Clean, Train 160 / Dev 40, Wayu ตัวเดียว ไม่มี Final Test
- Seed 42, microbatch 2 / accumulation 8 = effective batch 16, 10 updates ต่อ epoch (รวม 30)
- AdamW LR 1e-5 / weight decay 1e-4, clip norm 1, float32 ไม่มี AMP, CE ไม่ถ่วง class
- BN ใช้ running statistics เดิมทุก epoch แต่ affine parameters และน้ำหนักอื่นเรียนรู้ได้ Dropout เปิดตอนฝึก
- WAV mono 16 kHz ไม่แก้ไฟล์เต็ม เลือก 64,600 samples; Train seeded window เดิมคงที่ทั้ง 3 epochs, Dev ช่วงแรก, คลิปสั้น repeat
- Shuffle ต่อเนื่องตาม generator seed เดิม เปลี่ยนลำดับแต่ละ epoch ไม่ resample crop ไม่เพิ่ม scheduler/resume/early stopping

ใช้ windows เดิมโดยตั้งใจเพื่อเปลี่ยนปัจจัย epoch budget ก่อน ไม่อ้างว่าการ crop ครั้งเดียวทุก epoch เป็นสูตรเหมาะสมที่สุดสำหรับงานหลัก

## อ่าน Train loss / Dev loss อย่างไร

กราฟใช้ **Train evaluation loss** และ **Dev loss** ที่วัดใน `model.eval()` ทั้งคู่ (dropout ปิด, BN ไม่อัปเดต) จึงไม่ได้เอา loss ระหว่าง backward ซึ่งมี dropout มาปะปน

Train evaluation ใช้ seeded windows ที่ใช้ฝึก ส่วน Dev ใช้ช่วงแรกตาม policy เดิม ทั้งสองเป็น cross-entropy เฉลี่ยต่อคลิป หน่วย/ความหมายเดียวกัน แต่เป็นคนละชุดข้อมูล/กฎเลือก window ไม่ควรตีความความต่างว่าเกิดจาก overfit อย่างเดียว

`train_optimization_mean_loss` บันทึกแยกใน JSON เป็นค่าเฉลี่ยขณะกำลังฝึก น้ำหนักเปลี่ยนในระหว่าง epoch และ dropout เปิด จึงไม่ใช่เส้น Train evaluation ในกราฟ

การวัด Train เพิ่มและการสร้างโมเดลตรวจ reload ใช้ RNG-preserving context เพื่อไม่ให้การตรวจระหว่างทางเปลี่ยนการสุ่ม dropout ของรอบฝึกถัดไป

## สคริปต์และคำสั่ง

ใช้ [train_aasist_frozen_bn.py](../../scripts/aasist/train_aasist_frozen_bn.py) ไม่แก้สคริปต์ 1 epoch ที่ใช้สร้างผลเดิม รันจาก project root ด้วย `.venv` หลัก (ต้องมี matplotlib จาก environment ที่ใช้ EDA, data/upstream/pretrained เตรียมแยก):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\train_aasist_frozen_bn.py --run-id frozen3_my_run_01 --device cuda
```

Script จำกัด 3 epochs ไม่รับ `--epochs` เพื่อไม่ขยายงบโดยไม่ได้ตกลง ใช้ run-id ใหม่ ไม่ทับ/ลบ/backup ผลเก่า หากรันแล้วไม่ต้องรันซ้ำ หากล้มเหลวจะเก็บ `status: failed` และผลที่ได้ถึงตอนนั้น ไม่สร้างผลว่า completed

อัปเดตสำหรับการตรวจความแกว่ง: รับ `--seed` ได้ โดย default ยังเป็น 42 และสูตรอื่นไม่เปลี่ยน ดู [การตรวจสาม seeds](AASIST_SEED_STABILITY_TH.md) ผล seed 42 ที่รายงานด้านล่างยังคงเป็นผล/hashes เดิม ไม่ถูกเขียนใหม่

Helpers อยู่ `src/thai_spoof/pilot/learning_curve.py` ทดสอบ accumulation กลุ่มท้าย, BN ไม่เปลี่ยน, RNG-neutral evaluation/reload และการเลือก checkpoint จาก Dev เท่านั้น

## ไฟล์ผล

ผลอยู่ `results/pilot/aasist_frozen_bn_curve/<run_id>/` ไม่ขึ้น Git:

| ไฟล์ | หน้าที่ |
| --- | --- |
| `loss_curve.png` | กราฟ Train evaluation / Dev ตั้งแต่ epoch 0 (pretrained) ถึง 3 |
| `learning_curve.json` | ค่าของทุก epoch และ hash checkpoint/reload error |
| `run.json` | config/hash/source/environment/status/สรุปจำนวน updates/exposures/BN audit |
| `training_log.json` | loss ตอน backward/grad norms/ลำดับคลิปและ crop แต่ละ epoch |
| `scores.csv` | logits ของ Train/Dev แยก epoch รวม baseline ไม่ใช่ Test scores |
| `epoch_001.pt` ถึง `epoch_003.pt` | model/optimizer/config ของแต่ละ epoch พร้อมตรวจโหลดเข้าโมเดลใหม่ |
| `selection.json` | ชี้ checkpoint ที่ Dev CE ต่ำสุดใน epochs 1–3; เสมอกันเลือก epoch แรก |

Epoch 0 เป็น pretrained reference ไม่อยู่ในตัวเลือก "best trained epoch" หาก trained best ยังแย่กว่า pretrained จะบันทึกว่าไม่ได้ดีขึ้น ไม่เรียกว่าการฝึกสำเร็จด้าน performance

ไม่มีไฟล์ `best.pt`/`last.pt` ซ้ำเพิ่มเพื่อหลีกเลี่ยงสับสน `selection.json` ชี้ไฟล์ epoch ที่มีอยู่จริง CLI inference เดิมยังโหลด pretrained เดิม **ไม่โหลด checkpoint นี้ให้อัตโนมัติ** และยังไม่มี resume

## ผลรัน 8 ตุลาคม 2026

Run ID: `frozen3_20261008_v1` บน RTX 3050 Ti Laptop GPU:

| Epoch | Train evaluation CE | Dev CE |
| --- | --- | --- |
| 0 — pretrained | 1.785548 | 1.594355 |
| 1 | 1.477809 | 1.074124 |
| 2 | 0.972610 | 0.642973 |
| 3 | 0.530635 | 0.338209 |

ทั้ง Train evaluation และ Dev ลดลงครบสาม epochs ยังไม่เห็น Dev แย่ลงในงบนี้ แต่ไม่ได้พิสูจน์ว่าไม่มี overfit หรือ generalize ไปเสียงใหม่/TTS อื่นได้

- เลือก **epoch 3 เฉพาะในตัวเลือก epochs 1–3** ตาม Dev CE: `epoch_003.pt` และ pointer ใน `selection.json` ไม่ใช่ best model ที่ยืนยันแล้วของงานวิจัย
- รันครบ 30 updates / 480 exposures บน Train เดิม 160 คลิป มี parameters เปลี่ยน 154 tensors
- BN running buffers ไม่เปลี่ยนตลอดสาม epochs; checkpoint ทุก epoch โหลดเข้าโมเดลใหม่แล้ว max absolute Dev logit error 0
- Epoch 1 Dev CE ตรงกับ Frozen arm เดิม 1.074124 ไม่เอาผลเก่ามาเขียนเป็น epoch ใหม่
- เวลาประมาณ 51.15 วินาทีเฉพาะช่วงจับเวลา รวม evaluations/reloads/plot ไม่รวม audit/import/startup ทั้งหมด

กราฟอยู่ `results/pilot/aasist_frozen_bn_curve/frozen3_20261008_v1/loss_curve.png` ไม่ต้องรันซ้ำเพื่อเปิดดู

## ขอบเขตและขั้นถัดไป

ผลเป็น seed เดียว/3 epochs/200 คลิป/Wayu ระบบเดียว ใช้ Dev สำหรับพัฒนา recipe ไม่ใช่ Test accuracy/EER หรือผล Clean vs Mixed หาก Train ลดลงแต่ Dev เพิ่มขึ้นต้องตรวจแนวโน้มและปัจจัยอื่น ไม่สรุปว่า overfit จากตัวเลขเดียว

เมื่อดูผลแล้วค่อยกำหนดงบยืนยัน recipe/seed/cohort ก่อนขยายข้อมูลและ generators ไม่เพิ่มจำนวน epochs ต่อไปเรื่อย ๆ ตาม Dev โดยไม่มีงบ และไม่ใช้ Final Test เลือก recipe
