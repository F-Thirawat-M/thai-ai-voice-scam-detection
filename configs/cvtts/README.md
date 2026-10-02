# Configuration ของ workflow ใหม่

ยังไม่มี executable config/training pipeline ในโฟลเดอร์นี้ ให้สร้างใน T01 หลังตรวจ release/paths และยืนยันขอบเขต

ไฟล์เป้าหมาย:

- `protocol_v1.yaml`: policy ข้อมูล/split/audio/conditions/training/evaluation
- `tts_registry.yaml`: generator IDs, pinned revisions, voices, licenses, environments
- `runs/<model>_<arm>_seed<seed>.yaml`: resolved settings ของแต่ละ run

ตัวอย่าง YAML ใน [workflow ส่วน 20.3](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s20) เป็น draft มี placeholder โดยตั้งใจ ไม่ใช่ config พร้อมฝึก

Commit เฉพาะ configuration ที่ไม่มี credentials/ข้อมูลส่วนบุคคล ค่า local root override เก็บใน environment หรือ `.env` ที่ ignore; เก็บ resolved config พร้อม hashes ใน `results/cvtts/<protocol>/<run_id>/` ของการทดลองจริง
