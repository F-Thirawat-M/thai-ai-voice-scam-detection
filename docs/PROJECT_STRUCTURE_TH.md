# โครงสร้างโปรเจกต์หลังปรับแผน

ปรับวันที่ 3 ตุลาคม 2026 ใช้ Common Voice + TTS เป็น workflow หลัก โครงสร้าง inference สองโมเดลเดิมเหมาะสมอยู่แล้วจึงคงไว้ ส่วนข้อมูล/เอกสารเลิกยึด SEA-Spoof

## มีแล้วและยังใช้อยู่

| ตำแหน่ง | หน้าที่ |
| --- | --- |
| `src/thai_spoof/aasist/` | adapter, preprocessing, config และคู่มือ AASIST |
| `src/thai_spoof/rawnet2/` | network, adapter, config, checkpoint utilities และ license |
| `src/thai_spoof/cli.py` | infer/evaluate ของ pretrained baseline |
| `src/thai_spoof/metrics.py`, `prediction.py` | metrics/ผลทำนายเดิมที่ต้องพัฒนาต่อก่อน Final Test ใหม่ |
| `scripts/check_environment.py` | ตรวจ runtime/GPU/ไฟล์ AASIST |
| `scripts/create_smoke_audio.py` | สร้างเสียงสัญญาณทดสอบเส้นทาง inference |
| `scripts/setup.ps1` | bootstrap เครื่องใหม่ มีขั้นดาวน์โหลด/ติดตั้ง จึงไม่รันซ้ำโดยไม่อ่าน |
| `external/aasist/` | upstream source ที่ AASIST adapter import จริง ไม่ใช่ของเหลือที่ลบได้ |
| `checkpoints/aasist/`, `checkpoints/rawnet2/` | pretrained weights ที่ยังโหลดได้ |
| `tests/test_audio.py`, `tests/test_metrics.py` | baseline regression tests ไม่ใช่การรับรอง protocol ใหม่ |

## เตรียมพื้นที่แล้ว แต่ยังไม่มี pipeline

| ตำแหน่ง | งานที่จะสร้าง |
| --- | --- |
| `configs/cvtts/` | protocol, TTS registry, run configs |
| `src/thai_spoof/cvtts/` | shared audit/split/TTS/conditions/training/evaluation |
| `tests/cvtts/` | tests ของ pipeline ใหม่ |
| `data/exploration/common_voice/` | notebook EDA และ outputs |
| `data/raw/common_voice/`, `data/raw/noise/` | ข้อมูลต้นทางตาม source/release |
| `data/processed/cvtts/` | corpus/version, canonical/native audio, manifests, QC, jobs |
| `docs/decisions/`, `docs/reports/cvtts/` | decision log และรายงาน |

Raw/processed เป็น ignored local directories ไม่อยู่ใน Git; เมื่อ clone ใหม่ขั้น audit/setup ของ pipeline ต้องสร้างด้วย `mkdir(..., exist_ok=True)` ตาม config ไม่ต้องใส่ `.gitkeep` ลงในทุก dataset folder

## เส้นทางผลทดลองเมื่อเริ่มทำจริง

- Dataset หนึ่งรุ่น: `data/processed/cvtts/<version>/`
- Run config: `configs/cvtts/runs/<model>_<arm>_seed<seed>.yaml`
- Checkpoints: `checkpoints/<model>/cvtts/<run_id>/`
- Scores/logs/metrics: `results/cvtts/<protocol>/<run_id>/`
- รายงานเผยแพร่ได้: `docs/reports/cvtts/`
- ไฟล์ชั่วคราว: `tmp/<task-name>/` ห้ามใช้เป็นที่เก็บผลที่ไม่มีสำเนาอื่น

อย่าสับสน scaffold กับฟังก์ชันที่มีจริง: `scripts/cvtts_pipeline.py`, training modules และ YAML ที่รันได้ **ยังต้อง implement** ตาม [workflow ส่วน 20–21](COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s20)

## ไม่ใช้แล้ว

SEA-Spoof/Typhoon raw/processed/EDA, extract/audit scripts ของชุดเก่า, tests ที่ผูกกับ scripts เหล่านั้น และ `RESEARCH_PLAN_TH.md` เดิมถูกลบ ไม่สร้างโฟลเดอร์ legacy/archive ซ้ำ

`data/manifests/` ถูกเลิกใช้ เพื่อไม่ให้ manifest ต่าง dataset/version ปนกัน ตัวอย่าง schema ของ CLI เดิมอยู่ `examples/inference_manifest.csv` และข้อมูลจริงต้องอยู่ใต้ dataset version

ดู [รายการล้างและการกู้คืน](CLEANUP_2026-10-03.md) ถ้าต้องกลับไปดูงานเก่า ห้ามถือว่าข้อมูลที่ ignore จะกู้จาก Git ได้
