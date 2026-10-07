# Pilot: ลอง fine-tune AASIST Clean 1 epoch — อ่านผลครั้งแรก

## ขั้นนี้ทำอะไร

นำ pretrained AASIST ที่มีอยู่มาฝึกปรับน้ำหนักด้วยเสียงคนและ Wayu ใน pilot ไม่ใช่ train จากศูนย์ และไม่ใช่ inference อย่างเดียว ใช้ Train 160 คลิป (คน 80 / Wayu 80) กับ Dev 40 คลิป (คน 20 / Wayu 20) **ไม่มี Final Test** และยังไม่ฝึก RawNet2 หรือ Noise/Telephone

ความหมายของ Clean คือไม่เพิ่ม noise/telephone จำลอง ไม่ได้หมายความว่าไฟล์ Common Voice ไม่มีเสียงรบกวนเดิม

โค้ดโครงข่ายยังมาจาก `external/aasist/models/AASIST.py` ไม่ได้เขียน AASIST ใหม่ สิ่งที่เพิ่มในโปรเจกต์คือ:

- `src/thai_spoof/cvtts/windows.py`: เลือกช่วงเสียง 64,600 samples (4.0375 วินาที); Train สุ่มจุดเริ่มแบบรวมจุดท้าย, Dev ใช้ช่วงแรก, คลิปสั้นวนเสียงซ้ำ ทั้งสองคลาสใช้กฎเดียวกัน ไม่แก้เสียงเต็ม
- `src/thai_spoof/pilot/pilot_data.py`: ตรวจ hash/schema/counts/split/source path แล้วสร้าง Dataset จาก canonical WAV mono 16 kHz; โหลด Train/Dev เท่านั้น
- `experiments/pilot/scripts/aasist/train_aasist_clean.py`: forward/backward, gradient accumulation, optimizer update, บันทึก checkpoint/log/Dev scores และโหลดกลับเข้าโมเดลใหม่เพื่อตรวจความตรงกัน
- `tests/cvtts/test_windows.py`, `tests/pilot/test_pilot_data.py`: ตรวจ crop/pad ขอบเขต, class mapping, source/output hashes และ split overlap ด้วย fixture สัญญาณที่สร้างเอง ไม่ใช้ข้อมูลจริงเป็น fixture

## ค่าที่ใช้รอบแรก

เลือกค่าเพื่อเช็ก pipeline ยังไม่ใช่ recipe ที่พิสูจน์แล้วว่าดีที่สุด:

- น้ำหนักเริ่มต้น: `checkpoints/aasist/AASIST.pth` โหลด strict; ไฟล์นี้ไม่ถูกเขียนทับ
- 1 epoch = ผ่าน Train ครบ 160 คลิปครั้งเดียว; microbatch 2 = 80 microbatches
- รวม gradient 8 microbatches ต่อ update = effective batch 16; รวม 10 optimizer updates
- AdamW, learning rate `1e-5`, weight decay `1e-4`, LR คงที่, clip gradient norm 1.0
- float32 ไม่ใช้ AMP; Train seed 42, shuffle RNG แยกจาก crop RNG
- cross-entropy แบบไม่ถ่วงน้ำหนัก เพราะ pilot สมดุล; **ต่างจากต้นฉบับ upstream ที่มี class weights** ไม่อ้างว่าคัด training recipe ทางการมาทั้งหมด
- `spoof = 0`, `bonafide = 1` ตรวจจาก `external/aasist/data_utils.py`; คะแนน Dev คือ logit ของ bonafide ลบ logit ของ spoof ไม่ใช่ calibrated probability
- ไม่เพิ่ม frequency masking/noise/telephone และไม่ normalize gain จาก canonical; policy นี้ใช้สำหรับ feasibility smoke ต้องพิจารณาอีกครั้งก่อนล็อกการทดลองหลัก
- Crop Train หนึ่งครั้งต่อคลิปเพราะ script นี้รองรับ epoch เดียว; ยังไม่มี resampling ต่อ epoch, adaptive sampler, scheduler, best checkpoint หรือ resume

Gradient accumulation ไม่ได้ทำให้ BatchNorm มีพฤติกรรมเหมือน microbatch 16 จริง จึงต้องตรวจการฝึกด้วย microbatch เล็กก่อนนำไปใช้จริง

## เปิดดูผลที่เครื่องนี้

ผลอยู่ใน `results/pilot/aasist_clean_smoke/clean_epoch1_20261007_v1/`:

| ไฟล์ | เอาไว้ดูอะไร |
| --- | --- |
| `run.json` | สถานะ, settings, source/manifest/checkpoint/code hashes, loss, จำนวน updates, เวลาและ VRAM |
| `training_log.json` | loss ราย microbatch, gradient norm ราย update, ลำดับคลิปและตำแหน่ง crop |
| `dev_scores.csv` | คะแนน Dev ของ pretrained และหลัง smoke แยกเป็นสอง stage; ไม่มี Test scores |
| `last.pt` | น้ำหนักหลังฝึก, optimizer และ RNG บางส่วน สำหรับตรวจ/reload; ไม่ใช่ pretrained เดิม และยังไม่รองรับ resume |

ผลรัน 7 ตุลาคม 2026 บน RTX 3050 Ti Laptop GPU:

- ฝึกครบ 160 คลิป, 80 microbatches, 10 updates; 80 real / 80 spoof ถูกใช้ครบ
- มี parameter tensors เปลี่ยนจริง 155 ชุด; gradient และ parameters finite
- Dev cross-entropy loss: **ก่อน 1.594355 → หลัง 4.853433** (ค่าน้อยดีกว่า)
- โหลด checkpoint เข้าโมเดลใหม่แล้ว logits Dev ตรงกัน: max absolute error 0 ภายใน tolerance `rtol=1e-5, atol=1e-5`
- peak CUDA allocated ประมาณ 858 MiB, peak reserved ประมาณ 1,272 MiB; ไม่ใช่ RAM ทั้งระบบหรือข้อกำหนดขั้นต่ำของโมเดลทุกรอบ
- เวลาประมาณ 17.54 วินาที **เฉพาะช่วงที่จับเวลา รวม Dev ก่อน/หลังและ reload** ไม่รวม audit, import และ startup ทั้งหมด

**แปลผล:** pipeline ฝึกและ checkpoint ใช้งานได้ แต่รอบนี้ Dev loss แย่ลง ไม่สรุปว่าโมเดลตรวจแม่นขึ้นจากการที่ train สำเร็จ และไม่ใช่ผลวิจัย Clean vs Mixed หรือผลข้าม TTS ระบบอื่น ไม่รายงาน EER/accuracy จากรอบนี้แทน Final Test

มี preflight แยก `preflight_20261007_v1/` ใช้เพียง 4 Train คลิป 1 update แล้วกลับไปเริ่ม full epoch จาก pretrained เดิม ไม่ต่อยอดน้ำหนัก preflight มาเป็น full run

## ถ้าจะลองรันเอง

ต้องมี `.venv` หลัก, upstream AASIST/weights และ canonical pilot จาก notebooks บนเครื่องนี้ก่อน เครื่องเพื่อน `git pull` ได้โค้ด แต่ **ไม่ได้ dataset/checkpoint/run outputs ที่ ignore** ต้องเตรียมแยกตามคู่มือ

เปิด PowerShell ที่ project root:

```powershell
# ตรวจ unit tests ก่อน
.\.venv\Scripts\python.exe -m pytest -q

# ทดลองสั้น 4 Train คลิป (ใช้ชื่อใหม่ที่ยังไม่มี)
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\train_aasist_clean.py --run-id my_preflight_01 --device cuda --max-batches 2

# ครบ 1 epoch เริ่มใหม่จาก pretrained ไม่ต่อจาก preflight
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\train_aasist_clean.py --run-id my_clean_epoch1_01 --device cuda
```

อย่ารันซ้ำโดยใช้ run ID เดิม Script จะปฏิเสธ ไม่ลบ/เขียนทับ/backup run เก่า เมื่อเกิด error จะเก็บ `status: failed` หากสร้าง run directory แล้ว ไม่ควรเอา checkpoint ของ run ล้มเหลวมารายงานว่าเสร็จ

ตอนนี้ **ยังไม่ต้องรันเพิ่ม** เพื่อไล่ค่า loss ให้ดีขึ้น ดูผลรอบนี้และเข้าใจ Train/Dev ก่อน หากจะเปลี่ยน hyperparameters/window/gain ต้องบันทึกเป็น run ใหม่ ไม่แก้ผลเดิม

CLI `thai-spoof infer` เดิมยังใช้ pretrained config เดิม **ไม่ได้เลือก `last.pt` ให้อัตโนมัติ** อย่าใช้ผลทายจาก CLI เดิมอ้างว่าเป็นน้ำหนักหลัง fine-tune

## ขั้นถัดไปที่เหมาะสม

อัปเดต: ทำข้อ 1 แบบ fixed-input memorization ผ่านแล้ว ดู [ผลและข้อจำกัด](AASIST_OVERFIT_CHECK_TH.md) ไม่ได้อัปเดต/แทนที่ผล Dev ของรอบ smoke เดิม ขั้นต่อไปคือข้อ 2

1. ทำ overfit-small-batch test จาก Train เพื่อดูว่าโมเดลจำชุดเล็กได้และ label/loss/data flow สอดคล้องกัน ไม่ใช้ Dev เป็นชุดฝึก
2. ตรวจผลของ microbatch/BatchNorm และ recipe ด้วยงบ Train/Dev ที่บันทึกไว้; Dev loss ที่เพิ่มอย่างเดียวไม่ระบุสาเหตุแน่ชัด
3. เพิ่ม TTS ระบบที่สองและตรวจ corpus/split/QC ก่อนการเปรียบเทียบหลาย generators; Wayu ตัวเดียวรอบนี้ยังไม่ตรง scope หลัก
4. พัฒนา Noise/Telephone, training resume, Dev checkpoint/threshold และ EER ที่นิยามตรง workflow แล้วค่อยทำ Clean vs Mixed และ RawNet2 อย่างเทียบกันได้

นี่คือผ่านเฉพาะ smoke ด้าน technical forward/backward/reload ไม่ใช่ผ่าน Gate การทดลองเต็มตาม [workflow](../../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s14)
