# Configuration ของ workflow ใหม่

เพิ่ม [wayu-pilot-requirements.txt](wayu-pilot-requirements.txt) สำหรับ notebook ทดลอง Wayu 1 ข้อความ ใช้ environment **`.venv-wayu` Python 3.11** แยกจาก `.venv` หลัก ไม่ใช่ config ฝึก AASIST/RawNet2 ดู setup/ขอบเขตใน [README ของ notebook](../../experiments/pilot/docs/NOTEBOOK_DETAILS_TH.md#wayu-pilot)

[wayu-dataset-requirements.txt](wayu-dataset-requirements.txt) เพิ่ม English resource ที่ล็อกรุ่นไว้สำหรับ notebook สร้าง Wayu ครบ pilot Train 80 / Dev 20 เรียก `scripts/setup_wayu_pilot.ps1 -Dataset` ไม่ใช่ config ฝึก detector และไม่ติดตั้งลง `.venv` หลัก

ยังไม่มี executable config/training pipeline ในโฟลเดอร์นี้ ให้สร้างใน T01 หลังตรวจ release/paths และยืนยันขอบเขต

ไฟล์เป้าหมาย:

- `protocol_v1.yaml`: policy ข้อมูล/split/audio/conditions/training/evaluation
- `tts_registry.yaml`: generator IDs, pinned revisions, voices, licenses, environments
- `runs/<model>_<arm>_seed<seed>.yaml`: resolved settings ของแต่ละ run

ตัวอย่าง YAML ใน [workflow ส่วน 20.3](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s20) เป็น draft มี placeholder โดยตั้งใจ ไม่ใช่ config พร้อมฝึก

Commit เฉพาะ configuration ที่ไม่มี credentials/ข้อมูลส่วนบุคคล ค่า local root override เก็บใน environment หรือ `.env` ที่ ignore; เก็บ resolved config พร้อม hashes ใน `results/cvtts/<protocol>/<run_id>/` ของการทดลองจริง
