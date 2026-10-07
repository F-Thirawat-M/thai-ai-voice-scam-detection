# ส่งต่องานให้เพื่อน — โค้ดทาง Git ข้อมูลทาง ZIP

## แบ่งงานอย่างไร

| ส่วน | AASIST | RawNet2 | ใช้ร่วมกัน |
| --- | --- | --- | --- |
| สคริปต์ทดลองเล็ก | `experiments/pilot/scripts/aasist/` | `experiments/pilot/scripts/rawnet2/` (ยังไม่มี trainer) | — |
| คู่มือโมเดล | `experiments/pilot/docs/aasist/` | `experiments/pilot/docs/rawnet2/` | เอกสารอื่นใน `experiments/pilot/docs/` |
| Network/adapter | `src/thai_spoof/aasist/` | `src/thai_spoof/rawnet2/` | `src/thai_spoof/pilot/` และ `cvtts/` |
| น้ำหนักเริ่มต้น | `checkpoints/aasist/` | `checkpoints/rawnet2/` | ไม่ใช้ weights ข้ามโมเดล |
| ผล pilot | `results/pilot/aasist_clean_smoke/`, `aasist_overfit_check/` | `results/pilot/rawnet2/<run_id>/` (ยังไม่มี run) | — |
| Dataset/notebooks | — | — | `data/processed/cvtts/pilot_v1/`, `experiments/pilot/notebooks/` |

ไม่คัดลอก dataset เป็นสองชุด การเปรียบเทียบใช้ manifest/split/label และการเตรียมเสียงเดียวกัน ส่วนการปรับ recipe ของแต่ละโมเดลต้องบันทึกให้ชัด

## เพื่อนจะเห็นอะไรใน Git

เห็น source code, source notebooks ที่ไม่มี outputs, คู่มือ และโครงสร้างโฟลเดอร์จาก README/`.gitkeep` ซึ่งเป็นไฟล์ว่าง Git ไม่เก็บโฟลเดอร์เปล่าโดยตรง

**ไม่เห็นไฟล์จริง** ได้แก่ MP3/WAV/FLAC, metadata TSV, manifests CSV, QC JSON, model weights, ผลฝึก, executed notebooks และ ZIP การ pull โค้ดจึงไม่ได้ดาวน์โหลดเสียงหรือโมเดล

ไม่มีการส่งรายชื่อไฟล์เสียง/ข้อมูลผู้พูดขึ้น Git เพื่อทำแผนผัง แผนผังอธิบายชนิดไฟล์/ตำแหน่งเท่านั้น ดู [โครงสร้างทั้งหมด](PROJECT_STRUCTURE_TH.md)

## รับชุดข้อมูล pilot

1. Clone หรือ pull โค้ดที่มีการปรับโครงสร้างนี้แล้ว (ผู้ทำ AASIST ต้อง commit/push ก่อน เพื่อนจึงจะเห็นการเปลี่ยน)
2. รับ `cvtts_pilot_v1_for_rawnet2_20261007.zip` แยกจาก Git เป็นการส่งภายในทีมตามสิทธิ์ข้อมูล ไม่อัปโหลดสาธารณะ
3. แตก ZIP ลง project root ที่มี `pyproject.toml` ให้ `data/` อยู่ข้าง `src/` ไม่ซ้อน `project/project/` ถ้ามี pilot เดิมอยู่ ห้าม Replace All โดยไม่ตรวจ ใช้ clone ใหม่ได้
4. ตรวจไฟล์จาก project root:

```powershell
python _pilot_handoff\verify_package.py
```

ZIP มีข้อมูล pilot และ MP3 ต้นฉบับที่เลือกไว้ 100 คลิป พร้อมคู่มือและ checksum ไม่รวม Common Voice ทั้งชุด, metadata TSV ทั้งชุด, environment, weights หรือผลฝึก จึงใช้ข้อมูล pilot ได้ แต่ยังไม่พอสำหรับรัน EDA เต็มชุด/สร้าง TTS ใหม่ทั้งหมด

README/`.gitkeep` ที่เพิ่มภายหลังไม่เปลี่ยนไฟล์เสียงหรือ CSV ใน ZIP ตัวตรวจตรวจไฟล์ที่ระบุใน checksum ไม่ได้ห้ามไฟล์คู่มือส่วนเกิน แต่ก็ไม่ได้รับรองคุณภาพเสียงหรือสิทธิ์การใช้งาน

## เตรียม RawNet2 ต่อ

เพื่อนสร้าง environment ของตัวเอง ไม่คัดลอก `.venv`/`.venv-wayu` จากเครื่องนี้ Network/adapter เดิมอยู่ `src/thai_spoof/rawnet2/` ดู [คู่มือโมเดล](../src/thai_spoof/rawnet2/README.md) และเลือก dependency/device ให้เหมาะกับเครื่อง

เมื่อมี `.venv` หลักพร้อมแล้ว ใช้ตัวเตรียมน้ำหนักเดิม:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.rawnet2.setup_checkpoint
```

คาดว่าจะได้ `checkpoints/rawnet2/pre_trained_DF_RawNet2.pth` ซึ่งแยกจาก `checkpoints/aasist/AASIST.pth` ต้องมี network/สิทธิ์/การติดตั้งที่พร้อม การมี weights ไม่ได้เพิ่ม trainer ให้อัตโนมัติ

**งานที่ยังต้องทำ:** เพิ่ม RawNet2 trainer ใน `experiments/pilot/scripts/rawnet2/` ใช้ strict loader `src/thai_spoof/pilot/pilot_data.py`, window helpers ใน `src/thai_spoof/cvtts/windows.py`, Train 160 / Dev 40 (แต่ละ split สมดุลจริง/Wayu) ไม่ใช้ AASIST script โดยเปลี่ยนเพียงชื่อโมเดล

Canonical WAV เป็น mono 16 kHz เต็มความยาว; ขณะเข้าโมเดล pilot ใช้ 64,600 samples ตาม window policy ไม่ตัด/เขียนทับ WAV ต้นฉบับ ชุดนี้ยังไม่มี Final Test

เก็บ run ใหม่ใต้ `results/pilot/rawnet2/<run_id>/` ห้ามทับ run เดิม แยกคำสั่ง/settings/hash/ผล/reload ไว้ตรวจ เปรียบเทียบผลอย่างซื่อสัตย์ ไม่เอาความแม่นยำที่จำ Train มารายงานเป็นผลเสียงใหม่ และยังไม่เรียก pilot ว่างานวิจัยหลัก
