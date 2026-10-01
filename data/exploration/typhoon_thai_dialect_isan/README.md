# Typhoon Thai Dialect Isan — Metadata EDA

สำรวจ metadata ทุกแถวของ revision `dfc7e495b3069940880d184f0acfcc6b3cd4f364` ซึ่งตรงกับการตรวจ metadata รอบก่อน **ยังไม่ได้ดาวน์โหลด/ถอดรหัสเสียง** และไม่ใช้ผลนี้แทนการตรวจ waveform หรือ sample rate ของไฟล์จริง

## เปิดอ่านและรัน

เริ่มจากหัวข้อ 1–3 ของ [typhoon_isan_eda.ipynb](typhoon_isan_eda.ipynb) เพื่อดูจำนวนคอลัมน์, missing data และความครอบคลุมประชากร ก่อนอ่านการวิเคราะห์ละเอียด

ใน VS Code เลือก kernel `.venv` ของโปรเจกต์ แล้ว Run All หรือรันจาก project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[eda]"
.\.venv\Scripts\python.exe scripts\run_typhoon_isan_eda.py
```

ครั้งแรกใช้ HTTP byte ranges เพื่ออ่าน Parquet footer/schema และ **คอลัมน์ metadata ที่ไม่ใช่ audio** จาก 41 shards ไม่ใช้ `load_dataset` ที่อาจโหลดเสียงทั้งชุด และไม่บันทึก Parquet shards ต้นฉบับ

Metadata snapshot ที่มีเฉพาะคอลัมน์ที่อ่านเก็บใน:

```text
data/raw/typhoon_thai_dialect_isan/metadata/<revision>/
├── metadata.parquet
└── provenance.json
```

ครั้งต่อไปใช้ snapshot ในเครื่องหลังตรวจ SHA-256 และ revision จึงรัน offline ได้ หาก checksum ไม่ตรงหรือ cache ไม่สมบูรณ์ จะหยุดให้ตรวจ ไม่เขียนทับอัตโนมัติ

ผลในโฟลเดอร์นี้:

- `outputs/typhoon_isan_eda.executed.ipynb` — notebook ที่รันแล้ว มีตารางและกราฟ
- `outputs/typhoon_isan_eda.html` — รายงานอ่านได้โดยไม่ต้องรัน Jupyter
- `outputs/summary.json` — ตัวเลขสรุปและขอบเขต metadata-only
- `outputs/*.csv`, `*.png` — ตารางและกราฟ รวม missing data และ demographic conflicts

`data/raw/` และ `outputs/` ไม่เข้า Git เพราะมี metadata รายแถว/ข้อมูลประชากร Notebook source ต้องไม่มี cell outputs ก่อน commit

## สำรวจอะไรบ้าง

- จำนวนคอลัมน์ต้นทาง (รวม audio) เทียบคอลัมน์ metadata ที่อ่าน และคอลัมน์ provenance ที่เราเพิ่ม
- schema จริง, missing/null/blank แยกจาก gender=x (not specified)
- อายุ เพศ จังหวัด/อำเภอ และจุดตัด age × gender × province
- candidate speaker keys จาก filename ไม่ถือเป็นจำนวนคนยืนยัน
- จำนวนคลิป/ชั่วโมงต่อกลุ่มและต่อรหัส เพื่อดูความไม่สมดุล
- age/gender/residence conflicts ภายในรหัส ไม่เติมค่าเอง
- duration ตาม metadata, transcript/prompt/domain และ overlap ข้าม source Train/Test
- เทียบตัวเลขกับผลตรวจรอบก่อนเมื่อ revision ตรงกัน

## ข้อจำกัดที่ต้องรายงาน

ชุดนี้เป็น corpus เสียงตอบคำถามภาษาอีสานสำหรับ ASR ไม่มี label bonafide/spoof แบบ SEA-Spoof หากใช้เป็น external genuine-only test ต้องประกาศสมมติฐานเสียงจริงและสอบทานคุณภาพ/ที่มา ใช้วัด FRR ของเสียงจริงได้หลังล็อก threshold จาก Dev แต่ชุดเสียงจริงล้วนใช้คำนวณ EER ไม่ได้

province/district หมายถึง **ที่อาศัย** ตาม card ไม่ใช่ภูมิลำเนาหรือสำเนียงที่เราตรวจยืนยัน ไม่มีการทำนายอายุ/เพศจากเสียง ไม่อ้างว่าครอบคลุมทุกวัย/ทุกภาค และไม่อ้าง speaker-disjoint จาก ID คลิปไม่ซ้ำ

ยังไม่ได้ตรวจ actual audio headers, channels, sample rate, silence/clipping, file hashes, SNR หรือ model inference ใน notebook นี้

หน้า dataset ระบุ Apache-2.0 ใน header แต่เนื้อหา card ระบุ CC-BY-4.0 ต้องยืนยันเงื่อนไขกับผู้สร้างก่อนนำเสียงมาใช้/เผยแพร่จริง

แหล่ง: [Typhoon dataset card](https://huggingface.co/datasets/typhoon-ai/thai-dialect-isan-dataset)
