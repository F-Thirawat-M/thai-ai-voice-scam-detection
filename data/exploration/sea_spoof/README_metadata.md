# SEA-Spoof — Remote Metadata-only EDA

Notebook ใหม่: `sea_spoof_metadata_eda.ipynb` สำหรับสำรวจ **Train / Validation / Evaluation ครบทั้งสาม split** แบบเดียวกับ Typhoon Isan: อ่าน schema/metadata ไม่เลือกคอลัมน์ audio

## เปิดและรัน

ใน VS Code เปิด notebook แล้วเลือก kernel `.venv` ของโปรเจกต์ อ่านหัวข้อ 1–4 ก่อนเพื่อดู scope, จำนวนคอลัมน์, จำนวนคลิป และ missing data โดยไม่แสดงตาราง missing ซ้ำอีกชุด

จาก project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[eda]"
.\.venv\Scripts\hf.exe auth login
.\.venv\Scripts\python.exe scripts\run_sea_spoof_metadata_eda.py
```

ต้อง login ด้วยบัญชี Hugging Face ที่ได้รับอนุมัติ SEA-Spoof แล้ว ไม่ใส่ token ลง notebook/helper/Git หรือส่ง token มาในแชท การ login เป็นขั้นตอนของผู้ใช้ หากมีสิทธิ์และ login ไว้แล้วไม่ต้อง login ซ้ำ

## วิธีอ่านและไฟล์ที่เก็บ

- ครั้งแรกอ่าน **Hugging Face โดยตรง** ที่ revision `132f5dca9b6efe39cf1d3b54a858f167f5a421fc` ไม่เปิด/reuse Parquet ใน `data/raw/sea_spoof_hf/`, manifest หรือเสียงที่เตรียมไว้ก่อนหน้า
- อ่านทุกภาษาเพื่อสรุปภาพรวม แล้วเจาะ `language = th` สำหรับการวิเคราะห์รายละเอียด
- PyArrow อ่านเฉพาะ 17 metadata columns จาก schema 18 columns โดยไม่เลือก `audio` ใช้ HTTP ranges สำหรับ footer/schema และ metadata chunks ไม่ดาวน์โหลด complete shards
- ช่วง byte ของคอลัมน์ metadata ที่ติดกันถูกรวมเพื่อประหยัด HTTP requests ไม่รวมข้าม gap ซึ่งอาจมี audio; helper ปฏิเสธ read นอกช่วงที่กำหนด
- footer อาจมี incidental bytes ของข้อมูลท้ายไฟล์ จึงไม่อ้างว่าไม่มี audio-related bytes ผ่าน network แม้แต่ byte เดียว สิ่งที่ยืนยันได้คือไม่เลือก/ถอดรหัส/บันทึก audio และไม่บันทึก source shards เต็ม
- เพิ่ม `official_split` และ `source_parquet` 2 คอลัมน์เพื่อสืบย้อนต้นทาง รวม snapshot 19 columns
- Snapshot ใหม่: `data/raw/sea_spoof_metadata/<revision>/metadata.parquet` และ `provenance.json` (ทั้งหมด Git ignored)
- ครั้งถัดไป reuse ได้เฉพาะ snapshot ใหม่นี้เมื่อ revision, dataset, selected columns, scope และ SHA-256 ตรง ถ้าไม่ตรง/ไม่สมบูรณ์หยุด ไม่เขียนทับอัตโนมัติ

Metadata ใช้ RAM และ disk จริง ขนาดไม่เท่ากับ audio ทั้งชุด เวลาอ่านครั้งแรกขึ้นกับ network/HTTP requests ไม่รับประกันว่าจะเสร็จทันที

## ผลตรวจ metadata วันที่ 2 ตุลาคม 2026

อ่านครบ 38 remote shards / 553,746 แถวทุกภาษา แล้วพบภาษาไทย 85,215 คลิป:

| Split | bonafide | spoof | รวมคลิปไทย |
|---|---:|---:|---:|
| Train | 15,734 | 49,674 | 65,408 |
| Validation / Dev | 3,216 | 6,688 | 9,904 |
| Evaluation / Test | 3,216 | 6,687 | 9,903 |

Snapshot metadata ทุกภาษาขนาด 20.32 MB ไม่มี audio เทียบ counts กับ dataset card ของ revision นี้ตรงทั้งหมด รันซ้ำจาก snapshot ที่ตรวจ checksum แล้วได้โดยไม่อ่าน source shards ใหม่

ภาษาไทยครบสาม split: `speaker_or_voice` ว่าง 74,644 คลิป (87.59%); `source_dataset` ว่าง 63,049 (73.99%); `spoof_type` ว่าง 22,166 (26.01%) ซึ่งตรงกับจำนวนเสียงจริง ค่าว่างไม่จำเป็นต้องเป็นข้อผิดพลาดเสมอ ต้องตีความตาม label และ applicability

ไม่พบ row_id/utterance_id ซ้ำข้าม split ของไทย แต่พบข้อความและบางรหัส voice ร่วมกัน ไม่ยืนยันว่าเป็นเสียงซ้ำหรือคนเดียวกัน และยังพิสูจน์ speaker-disjoint ไม่ได้ ไม่มีการตรวจ hash เสียงใน notebook ใหม่นี้

**Train metadata สำรวจแล้ว ไม่ได้แปลว่าดาวน์โหลดเสียง Train แล้ว หรือเทรนโมเดลแล้ว** ผลรันใหม่มี 27 CSV tables, 4 PNG figures และรายงาน HTML

## ผลใหม่แยกจากรายงานเสียงเดิม

เก็บใน `outputs/metadata_only/`:

- `sea_spoof_metadata_eda.executed.ipynb` — notebook พร้อมผล
- `sea_spoof_metadata_eda.html` — รายงานอ่านได้ทันที
- `summary.json` — scope, counts, missing, overlaps, versions
- CSV tables และ PNG figures

ไม่เขียนทับ `outputs/sea_spoof_eda.*` หรือ `outputs/summary.json` ของ notebook เดิม ถ้ารันผิดพลาด runner เก็บ `sea_spoof_metadata_eda.failed.ipynb` เพื่อวินิจฉัยเท่านั้น ไม่ใช่รายงานสำเร็จ

## สิ่งที่ตอบได้ / ไม่ได้

ตอบได้: schema จริงและความหมาย, counts แยกภาษา/split/label, missing (null/blank แยกกัน; ไม่ถือ False/0/none เป็น missing), sources, transcript provenance/length, candidate voice codes และ ID/text/code overlap ข้าม split

ตอบไม่ได้: อายุ/เพศ/จังหวัด/สำเนียง (ไม่มีใน schema), จำนวนคนที่ยืนยันแล้ว, duration/hours (ไม่มี duration และไม่อ่านเสียง), sample rate/channels จาก header, silence/clipping/SNR, เสียงซ้ำจาก file hash, EER/inference/training

ชื่อ `source_model` เป็นระบบสร้างเสียงปลอม ไม่ใช่ detector ของเรา ข้อความเดียวกันอาจเป็นคู่จริง–ปลอม รหัสชื่อเดียวกันข้ามระบบไม่ยืนยันคนเดียวกัน และ ID คลิปไม่ซ้ำไม่ยืนยัน speaker-disjoint ไม่มีการเปลี่ยน split/ลบข้อมูลอัตโนมัติ

## Colab และสิทธิ์เผยแพร่

Notebook นี้ใช้ helper ใน repository จึงไม่ใช่ standalone upload-and-run ใน Colab ต้องนำ notebook/helper ไปพร้อมกัน ตั้ง root ให้ถูกและ login HF แยกใน runtime ไม่สามารถอ่าน D: โดยตรง

ผลและ raw metadata ไม่เข้า Git ตาม `.gitignore` เพราะเป็นข้อมูลมีข้อจำกัด ห้ามเผยแพร่กับผู้ไม่มีสิทธิ์ Notebook source ต้อง Clear All Outputs ก่อน commit; runner รักษา source สะอาด ไม่มีการ commit/push ให้

แหล่ง: [SEA-Spoof dataset card](https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof)
