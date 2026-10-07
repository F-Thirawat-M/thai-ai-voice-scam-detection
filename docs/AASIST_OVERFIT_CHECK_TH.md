# ทดลองให้ AASIST จำ Train ชุดเล็ก

## ทำไปเพื่ออะไร

รอบ Clean 1 epoch เดิมยืนยันว่าฝึกและ reload ได้ แต่ Dev loss เพิ่ม จึงตรวจเส้นทางการเรียนรู้ด้วย **Train ชุดเล็กที่ฝึกซ้ำ** ก่อนขยายงาน

การตั้งใจให้จำชุดเล็กในขั้นนี้เป็น diagnostic ไม่ใช่เป้าหมายการทดลองหลัก และไม่ใช่การวัดกับเสียงใหม่ ถ้าโมเดลจำชุดเล็กไม่ได้ ต้องตรวจข้อมูล/labels/loss/gradient/optimizer ก่อน แต่ถ้าจำได้ก็ยังไม่ได้รับประกัน generalization หรือระบุสาเหตุ Dev loss เดิมได้

## ข้อมูลและวิธีทดลอง

- เลือก 2 คู่ข้อความจาก Train: เสียงคน 2 + Wayu 2 = **4 คลิปไม่ซ้ำ** เลือกด้วย seed 42 จาก source IDs ที่เรียงลำดับ ไม่เลือกด้วยคะแนนโมเดล ไม่ใช้ Dev/Test
- ตรวจ Train manifest, source/audio/waveform hashes และ canonical WAV mono 16 kHz ตาม loader เดิม
- เลือกช่วง 64,600 samples (4.0375 วินาที) ด้วย seed เดิมหนึ่งครั้ง แล้วใช้ **tensor เดิมทุก update**; คลิปสั้น repeat โดยไม่เขียนเสียงเต็มใหม่
- เริ่มจาก `checkpoints/aasist/AASIST.pth` เดิม ไม่ต่อจาก checkpoint ที่ Dev loss แย่ลง และไม่เขียนทับ pretrained
- ใช้ model **eval mode แต่เปิด autograd**: ปิด dropout และไม่อัปเดต running statistics ของ BatchNorm แต่ parameter ทุกตัว รวม affine parameters ของ BatchNorm ยังเรียนรู้ได้
- AdamW LR `1e-4`, weight decay 0, unweighted cross-entropy, float32, clip gradient norm 1.0
- Microbatch 2 × accumulation 2 = effective subset batch 4 ต่อ update; ใช้ sum CE / จำนวนทั้งหมดเพื่อถ่วงแต่ละคลิปเท่ากัน
- ตรวจชุดเดิมทุก 5 updates งบสูงสุด 100 updates หยุดเมื่อครบอย่างน้อย 20 updates และ **accuracy ของชุดที่ฝึก = 100% กับ loss ≤ 0.1** กฎนี้กำหนดก่อนรัน ไม่เลือกด้วย Dev
- เมื่อจบ ตรวจว่า parameters เปลี่ยน, buffers ไม่เปลี่ยน และ reload checkpoint เข้าโมเดลใหม่แล้ว logits ตรงกัน

**ค่ารอบนี้ต่างจาก smoke เดิมทั้ง mode/LR/weight decay/ข้อมูล** เพื่อเช็กการจำแบบคงที่ ไม่ใช่ controlled comparison และไม่สรุปว่า BatchNorm หรือ learning rate เป็นสาเหตุ Dev loss เดิม หรือว่าค่ารอบนี้เป็น recipe สำหรับงานวิจัยหลัก

## ผลที่รัน 7 ตุลาคม 2026

Run: `results/cvtts/aasist_overfit_check/fixed4_20261007_v1/`

| Update | Loss บน 4 คลิปเดิม | Accuracy บน 4 คลิปเดิม |
| --- | --- | --- |
| 0 | 3.375760 | 50% |
| 5 | 0.791914 | 75% |
| 10 | 0.108404 | 100% |
| 15 | 0.011889 | 100% |
| 20 | 0.002260 | 100% |

ผ่านเกณฑ์จำชุดเล็กที่ update 20 มี parameters เปลี่ยน 155 tensors, buffers ที่ตรึงไว้ไม่เปลี่ยน และ fresh-model reload มี max absolute logit error 0 ภายใน `rtol=1e-5, atol=1e-5`

ใช้ 4 คลิปซ้ำ 20 updates = **80 clip exposures ไม่ใช่ข้อมูลใหม่ 80 คลิป** ใช้ประมาณ 10.67 วินาทีในช่วงจับเวลา รวม subset evaluation/reload ไม่รวม startup/audit ทั้งหมด

**ความหมาย:** โมเดลเรียนรู้จนจำ 4 คลิปนี้ได้ ภายใต้ diagnostic settings เท่านั้น ไม่ใช่ accuracy 100% ของระบบกับเสียงใหม่ ไม่มี EER, Dev/Test scores หรือข้อสรุป Clean vs Mixed และยังไม่ได้พิสูจน์คุณภาพ/label ของทุกคลิปใน dataset

## โค้ดและไฟล์ที่เพิ่ม

- `src/thai_spoof/cvtts/overfit.py`: เลือกคู่ Train, ฝึก tensor คงที่, ตรวจ loss/gradients, เกณฑ์หยุด
- `scripts/check_aasist_overfit.py`: audit/โหลด pretrained/เรียก diagnostic/บันทึกผลและตรวจ fresh-model reload
- `src/thai_spoof/cvtts/provenance.py`: ตรวจ code hash เดิมแบบ exact หรือยอมรับเฉพาะ CRLF→LF เมื่อ Git Windows เปลี่ยนรูปแบบบรรทัด บันทึกวิธีตรวจไว้ใน run; ถ้าเนื้อหาอื่นเปลี่ยนจะหยุด **audio/manifest hashes ยัง byte-exact**
- `scripts/train_aasist_pilot.py`: แก้เฉพาะการตรวจ preparation code ให้ใช้ helper ข้างบน ไม่เปลี่ยน recipe/ข้อมูล/ผล smoke เก่า
- `tests/cvtts/test_overfit.py`, `test_overfit_guard.py`, `test_provenance.py`: ตรวจ paired selection/Train-only/ไม่ทับ run, gradient/BN/dropout, accumulation, checkpoint reload ด้วยโมเดลจำลอง และการปฏิเสธเนื้อหาโค้ดที่เปลี่ยนจริง

ไม่ได้แก้โครงข่าย upstream หรือไฟล์ข้อมูล/pretrained เดิม ไม่ commit/push อัตโนมัติ Branch คือ `feat-aasist-overfit-check`

## เปิดดูผลในเครื่อง

| ไฟล์ใน run directory | หน้าที่ |
| --- | --- |
| `run.json` | settings, คลิปที่เลือก, crop/window/source hashes, เกณฑ์ผ่าน, ผลสรุป, checkpoint hash |
| `training_log.json` | backward loss/gradient ทุก update และ fixed-subset metrics ทุก 5 updates |
| `subset_scores.csv` | label/logits/prediction ของ **4 คลิป Train** ก่อนและหลังจำ ไม่ใช่ Dev/Test |
| `last.pt` | น้ำหนัก diagnostic และ optimizer; ยังไม่มี resume ไม่ใช้เป็น final model |

ข้อมูลและผลฝึกถูก ignore ไม่เข้า Git เพื่อน pull ได้เฉพาะโค้ด/คู่มือ/tests ต้องเตรียม canonical pilot/weights บนเครื่องเพื่อนก่อนใช้

## คำสั่งสำหรับลองเองภายหลัง

รอบนี้รันให้แล้ว **ไม่ต้องรันซ้ำทันที** หากจะรันใหม่ต้องใช้ชื่อที่ยังไม่มีและ `.venv` หลัก ไม่ใช่ `.venv-wayu`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\check_aasist_overfit.py --run-id fixed4_my_run_01 --device cuda --max-updates 100
```

Script ปฏิเสธ run directory เดิม ไม่ลบ/backup/เขียนทับ ถ้ารันจบแต่ไม่ผ่านเกณฑ์ จะบันทึก `status: completed` และ `diagnostic_passed: false` ไม่สร้างผลว่าเรียนรู้สำเร็จ ถ้าเกิด runtime error หลังสร้าง run จะเก็บ `status: failed` และ log ที่ได้ถึงตอนนั้น ไม่มี resume

CLI inference เดิมยังโหลด pretrained เดิม ไม่ได้เลือก checkpoint diagnostic ให้อัตโนมัติ

## ต่อจากนี้

ยังอยู่ใน **pilot ก่อนการทดลองจริง** ขั้นต่อไปคือเช็ก recipe กับ Train/Dev แบบมีงบและบันทึก run เช่น ค่อยแยกตรวจผล BatchNorm/microbatch โดยเปลี่ยนทีละปัจจัย ไม่เอาน้ำหนักที่จำ 4 คลิปไปต่อยอดเป็น main run และไม่แก้ recipe หลายตัวพร้อมกันแล้วอ้างสาเหตุ จากนั้นค่อยเพิ่ม generator/conditions/main experiments ตาม [workflow](COMMON_VOICE_PROJECT_WORKFLOW_TH.md)
