# Thai Synthetic Speech Detection

โครงงานเปรียบเทียบ AASIST กับ RawNet2 เพื่อตรวจเสียงสังเคราะห์ภาษาไทยจาก Common Voice + TTS และเปรียบเทียบการฝึก Clean กับ Mixed (clean / noise / telephone)

## ตอนนี้อยู่ตรงไหน

**อยู่ใน pilot ก่อนการทดลองวิจัยจริง** เตรียมข้อมูลเล็กและลองฝึก AASIST แล้ว ยังไม่ทำ Final Test หรือเปรียบเทียบสี่แบบหลัก

- Clean 1 epoch: ฝึกได้ แต่ Dev loss เพิ่ม 1.59 → 4.85
- จำ Train 4 คลิป: ผ่านที่ 20 updates; 100% บนคลิปที่ฝึกซ้ำ ไม่ใช่ความแม่นยำกับเสียงใหม่
- ขั้นถัดไป: ตรวจ recipe ด้วย Train/Dev โดยเปลี่ยนทีละปัจจัย

## เปิดอ่านจากตรงนี้

| ถ้าต้องการ | เปิด |
| --- | --- |
| ทำงานต่อจากตอนนี้ | [Pilot — หน้าเริ่มต้น](experiments/pilot/README.md) |
| เข้าใจว่าแต่ละโฟลเดอร์คืออะไร | [แผนผังไฟล์](docs/PROJECT_STRUCTURE_TH.md) |
| ดูขอบเขตงานวิจัยจริงที่ยังไม่เริ่ม | [Research — สถานะและแผน](experiments/research/README.md) |
| อ่าน workflow วิจัยละเอียด | [Workflow หลัก](docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md) — มีคำสั่ง proposed ที่ยังรันไม่ได้ |

## แยกเป็น 4 ส่วน

```text
experiments/pilot/       notebook / คำสั่ง / คู่มือทดลองเบื้องต้น
experiments/research/    ขอบเขตงานจริง (ตอนนี้มีแผน ยังไม่มี trainer พร้อมใช้)
src/thai_spoof/          โค้ดโมเดลและ helpers ที่โปรแกรมใช้
data/ + results/         ข้อมูลและผลในเครื่อง ไม่เข้า Git
```

ข้อมูล pilot อยู่ `data/processed/cvtts/pilot_v1/`; ผลฝึก pilot อยู่ `results/pilot/` ไม่ใช้เป็น main experiment หรือ Final Test

Tests: `.\.venv\Scripts\python.exe -m pytest -q`

Branch ตาม feature ไม่ใช้ `codex/`; ผู้ใช้ commit/push เอง การ pull โค้ดไม่ได้ดาวน์โหลด dataset/weights/results ที่ ignore ให้

ที่มาโมเดล: [AASIST](https://github.com/clovaai/aasist) / [RawNet2 integration](https://github.com/Nattadol/thai-audio-deepfake) เก็บ attribution/license ไว้เหมือนเดิม
