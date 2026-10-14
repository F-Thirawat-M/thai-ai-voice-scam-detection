# CLAUDE.md — กติกาสำหรับ Claude Code ใน repository นี้

โครงงานสัมมนาปี 3 (KKU): จำแนกเสียงมนุษย์และเสียงสังเคราะห์ AI ภาษาไทยสำหรับป้องกันมิจฉาชีพทางโทรศัพท์
ผู้ใช้ (Boy) รับผิดชอบ AASIST; เพื่อนรับผิดชอบ RawNet2 อธิบายเป็นภาษาไทย ทีละขั้น พร้อมผลตรวจที่ดูได้

## อ่านก่อนเริ่ม

1. `docs/RESEARCH_PROTOCOL_V2_TH.md` — **สมมติฐาน ตัวแปร และค่าที่ล็อกแล้ว (ยึดอันนี้เมื่อขัดกับ workflow)**
2. `docs/PROJECT_HANDOFF_2026-10-14_TH.md` — สถานะล่าสุดและสิ่งที่ทำแล้วจริง
3. `docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md` — แผนงานหลัก/protocol (เป็นแผน ไม่ใช่ผล)
4. `docs/decisions/CVTTS_DECISIONS.md` — การตัดสินใจและเรื่องที่ยังรอยืนยัน
5. `experiments/pilot/README.md` — pilot ที่ทำแล้วและขั้นถัดไป
6. ถ้างานเกี่ยวกับ voice cloning: `experiments/pilot/docs/cloning/CLONING_PILOT_BRIEF_TH.md`

## แกนการทดลอง (รายละเอียดใน protocol v2 — อย่าเปลี่ยนโดยไม่มี decision log)

- ตัวแปรต้น: สภาพข้อมูลที่ใช้ fine-tune — `orig` (เสียงต้นฉบับอย่างเดียว) vs `mct` (หลายสภาพ: original / noise 10,5 dB / simulated telephone)
- ทำซ้ำบน AASIST และ RawNet2 (ไม่ใช่การแข่งสองโมเดล)
- ตัวแปรตาม: EER บน Test แยกสภาพเสียง
- เสียงปลอม: voice cloning (G1 F5-TTS-THAI, G2 OmniVoice) ตัวแปรของ generator ทั้งหมดเป็นตัวแปรควบคุม: สร้างครั้งเดียว freeze ใช้ไฟล์ชุดเดียวกันทุกสูตร

## ห้ามทำ

- ห้าม commit / push / merge — ผู้ใช้ทำเอง ห้ามใช้ branch prefix `codex/`; ใช้ชื่อ feature เช่น `feat-cloning-pilot`
- **ห้ามให้ Claude/AI ปรากฏเป็น contributor เด็ดขาด**: ถ้าผู้ใช้สั่งให้ช่วยเขียน commit message หรือ PR description ห้ามใส่ `Co-Authored-By: Claude ...`, `Generated with Claude Code`, ลิงก์ session หรือ trailer/ข้อความ attribution ใด ๆ ของ AI; ห้ามตั้ง git `user.name`/`user.email` เป็นชื่อ AI; ใช้ตัวตน git ของผู้ใช้เท่านั้น
- ตรวจ `git status --short --branch` ก่อนเริ่มทุกครั้ง ห้ามทับงานที่ยังไม่ commit
- ห้ามทับหรือลบ: `data/`, `checkpoints/` (pretrained), `results/pilot/` (ผลเก่า), ZIP ส่งต่อ, `tmp/wayu-python`
- ทุก run ใช้ run-id ใหม่ (สคริปต์ปฏิเสธโฟลเดอร์ที่มีอยู่โดยตั้งใจ — ห้ามแก้ guard)
- ห้ามติดตั้ง/อัปเกรด package ลง `.venv` หลักเพื่อ TTS; TTS แต่ละตัวใช้ `.venv-<ชื่อ>` แยก (เหมือน `.venv-wayu`)
- ห้ามใช้ Final Test เลือก/ปรับอะไร; pilot ยังไม่มี Test และ Dev pilot ถูกใช้พัฒนาไปแล้ว
- clone ผู้พูด Common Voice ได้เพื่อการวิจัยตรวจจับ (ผู้ใช้อนุญาต 14 ต.ค.) แต่ห้ามพยายามระบุตัวตนผู้พูด
- ห้ามเผยแพร่/commit เสียงที่สร้าง เสียงต้นแบบ หรือ metadata รายคลิป
- ห้ามรายงานว่าทำสำเร็จจากแผนในเอกสาร — ต้องมีไฟล์ผลจริง

## วิธีทำงาน

- Environment หลัก: `.\.venv\Scripts\python.exe` (Python 3.12, Torch 2.11.0+cu128, RTX 3050 Ti 4 GB)
- Tests: `.\.venv\Scripts\python.exe -m pytest -q` ต้องผ่านก่อนและหลังแก้โค้ด
- Pin model ID + revision ของทุก model ที่โหลด; บันทึก seed/voice/parameters/hash ต่อคลิปตามแบบ manifest เดิม `data/processed/cvtts/pilot_v1/manifests/tts_wayu_train.csv`
- แยกโค้ด upstream (`external/aasist`, model ของเพื่อน) ออกจากโค้ดที่เขียนเพิ่ม และบอกผู้ใช้ทุกครั้งว่าส่วนไหนเป็นของใคร
- จบแต่ละงาน: รายการไฟล์ที่แก้, คำสั่งที่ใช้ตรวจ + ผล, สิ่งที่ยังไม่ได้รัน/ความเสี่ยง, งานถัดไป
- แยกสถานะให้ชัด: ทำเสร็จและตรวจแล้ว / เขียนแล้วแต่ยังไม่รัน / ติด blocker
