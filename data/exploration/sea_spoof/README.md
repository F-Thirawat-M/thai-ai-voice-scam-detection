# สำรวจข้อมูล SEA-Spoof (EDA)

โฟลเดอร์นี้เก็บเฉพาะ notebook, helper และผลสำรวจของ SEA-Spoof ไม่ผสมกับ dataset อื่น ข้อมูลชุดเดียวสามารถใช้เปรียบเทียบหลายโมเดลได้โดยไม่ต้องทำสำเนาแยกตามโมเดล

## เลือก notebook ตามขอบเขต

- `sea_spoof_metadata_eda.ipynb` — **ใหม่: metadata จาก Hugging Face ครบ Train/Validation/Evaluation ไม่ใช้ dataset เดิมในเครื่อง ไม่โหลดเสียงทั้งชุด** ดู [วิธีรันและข้อจำกัด](README_metadata.md); ผลแยกใน `outputs/metadata_only/`
- `sea_spoof_eda.ipynb` — เดิม: ตรวจ source/manifest และเสียงที่มีในเครื่อง (ขณะทำรายงานมีเฉพาะ Validation/Evaluation) คำอธิบายด้านล่างเป็นของ notebook เดิม

## เปิดใน VS Code

1. เปิด `sea_spoof_eda.ipynb`
2. เลือก **Select Kernel → Python Environments → .venv** ของโปรเจกต์
3. อ่านคำอธิบายและรัน cell จากบนลงล่าง หรือเลือก **Run All**

ติดตั้ง dependency จาก project root หากยังไม่มี:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[eda]"
```

## รันอัตโนมัติและดูรายงานพร้อมผล

```powershell
.\.venv\Scripts\python.exe scripts\run_sea_spoof_eda.py
```

ใช้ Python ตัวที่รันคำสั่งนี้เป็น kernel โดยตรง และเก็บผลไว้ใน:

- `outputs/sea_spoof_eda.executed.ipynb` — notebook ที่รันแล้ว มีตารางและกราฟ
- `outputs/sea_spoof_eda.html` — รายงานอ่านได้โดยไม่ต้องรัน Jupyter
- `outputs/summary.json` — scope, ตัวเลขสรุป, seed, เวอร์ชัน dependency และหลักฐาน source/manifest
- `outputs/*.csv` และ `*.png` — ตารางตรวจคุณภาพและกราฟ

ค่าเริ่มต้นอ่าน metadata ทุกแถวใน Parquet ที่มีในเครื่อง ตรวจ header และ hash ของเสียงไทยทุกไฟล์ ส่วน waveform metrics สุ่มไม่เกิน 60 คลิปต่อ split × label ด้วย seed คงที่ พร้อมรายงาน coverage จึงไม่อ้างว่าสำรวจ waveform ทั้ง dataset

หากต้องการถอดรหัสสัญญาณเสียงไทยทุกคลิป:

```powershell
.\.venv\Scripts\python.exe scripts\run_sea_spoof_eda.py --signal-all
```

อาจใช้เวลาหลายนาที แต่ประมวลผลทีละ block ไม่โหลดเสียงทั้งหมดเข้า RAM พร้อมกัน ต้องการข้าม file hash เพื่อรันเร็วขึ้นใช้ `--no-audio-hashes`; notebook จะระบุว่าข้าม ไม่สรุปว่าไม่มีเสียงซ้ำ

## Notebook สำรวจอะไรบ้าง

- inventory, schema, data dictionary และเวอร์ชันข้อมูลจาก HF download cache ถ้ามี
- ทุกภาษาใน local Parquet แล้วเจาะเสียงไทยแยกตาม official split
- ตรวจความครบถ้วนของ manifest เทียบ source และ metadata ไม่ตรงกัน
- missing values แยกตาม label และข้อจำกัดด้านอายุ/เพศ/ถิ่น/รหัสผู้พูด
- ความสมดุล label, source_dataset, source_model, online/offline และ synthetic voice values
- transcript length/provenance/exactness และ overlap ของ ID/text ข้าม split
- ไฟล์ที่อ่านไม่ได้, sample rate, channels, format, duration, ชั่วโมงและขนาดไฟล์
- SHA-256 ซ้ำภายใน/ข้าม split และ hash เดียวมี label ขัดแย้ง
- ผลของ crop/repeat-pad ที่ input window 64,600 samples (4.0375 วินาที)
- RMS/dBFS, near-zero, near-full-scale, DC offset, zero crossings ในขอบเขตที่ระบุ
- ตัวอย่าง waveform, spectrum, spectrogram; ฟังเสียงได้เมื่อเปิด `PLAY_AUDIO` เอง

## การตีความและสิทธิ์ข้อมูล

อ่านเฉพาะไฟล์ในเครื่อง ไม่ดาวน์โหลด ไม่ฝึกโมเดล ไม่เลือก threshold และไม่แก้ split หรือไฟล์ต้นฉบับ
จำนวนคลิปไม่ใช่จำนวนบุคคล `speaker_or_voice` อาจเป็น synthetic voice ส่วน text ซ้ำไม่เท่ากับ audio leakage เสมอไป การไม่มี file hash ซ้ำไม่ยืนยันว่า speaker-disjoint

ผลสำรวจและ notebook ที่รันแล้วถูก `.gitignore` เพราะอาจมี restricted metadata / audio-derived data ไม่ควรเผยแพร่โดยไม่ตรวจเงื่อนไขการใช้ SEA-Spoof
Notebook source ที่เก็บใน Git ต้องไม่มี cell outputs โดยเฉพาะ transcript หรือเสียงฝัง หากกด Run All ใน source ให้ Clear All Outputs ก่อน commit หรือใช้ runner ด้านบนเพื่อเก็บ source สะอาด

แหล่งคำอธิบาย: [SEA-Spoof dataset card](https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof)
