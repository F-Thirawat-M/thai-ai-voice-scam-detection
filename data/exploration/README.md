# สำรวจข้อมูลเสียง แยกตาม dataset

แต่ละ dataset มีโฟลเดอร์ของตัวเองสำหรับ notebook, helper ที่เฉพาะชุดข้อมูล, คู่มือ และผลสำรวจ ไม่แยกสำเนาข้อมูลตามโมเดล เพราะ AASIST, RawNet2 หรือโมเดลอื่นอาจใช้ dataset เดียวกันเพื่อเปรียบเทียบ

```text
data/exploration/
├── README.md
├── sea_spoof/
│   ├── README.md
│   ├── sea_spoof_eda.ipynb
│   ├── sea_spoof_eda_utils.py
│   └── outputs/                  # ผลที่รันแล้ว; ไม่เข้า Git
└── typhoon_thai_dialect_isan/
    ├── README.md
    ├── typhoon_isan_eda.ipynb     # metadata-only; ไม่โหลดเสียง
    ├── typhoon_eda_utils.py
    └── outputs/                  # ผลที่รันแล้ว; ไม่เข้า Git
```

- [SEA-Spoof notebook](sea_spoof/sea_spoof_eda.ipynb) และ [วิธีรัน](sea_spoof/README.md)
- [Typhoon Isan notebook](typhoon_thai_dialect_isan/typhoon_isan_eda.ipynb) และ [วิธีรัน/ขอบเขต metadata-only](typhoon_thai_dialect_isan/README.md)

เมื่อเพิ่ม dataset ใหม่ ให้สร้าง `data/exploration/<dataset_name>/` แล้วเก็บ notebook และ helper ของชุดนั้นภายใน พร้อมผลใน `outputs/` ที่ถูก gitignore โดยใช้ชื่อ snake_case

ไฟล์เสียง/Parquet ต้นฉบับยังแยกใน `data/raw/<dataset_name>/`, ข้อมูลที่ประมวลผลใน `data/processed/<dataset_name>/` ตามโครงสร้างของแต่ละ pipeline ไม่ย้ายต้นฉบับมาไว้ใน exploration และไม่เปลี่ยนโครงสร้างข้อมูลเดิมโดยไม่ปรับ pipeline ที่อ้างถึง

Notebook ที่มีเสียง/transcript หรือผลรายแถวต้องตรวจสิทธิ์ก่อนเผยแพร่ และ Clear All Outputs ก่อน commit notebook source คำสั่งรัน SEA-Spoof เดิมยังใช้ได้:

```powershell
.\.venv\Scripts\python.exe scripts\run_sea_spoof_eda.py --signal-all
```

รัน Typhoon Isan แบบอ่านเฉพาะ metadata (ครั้งแรกต้องใช้อินเทอร์เน็ต; ไม่อ่านคอลัมน์ audio):

```powershell
.\.venv\Scripts\python.exe scripts\run_typhoon_isan_eda.py
```
