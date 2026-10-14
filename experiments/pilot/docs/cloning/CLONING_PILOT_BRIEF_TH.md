# บรีฟงาน pilot: Voice cloning feasibility

สร้าง: 14 ตุลาคม 2026 · ปรับ: 14 ตุลาคม 2026 (อนุญาต clone ผู้พูด Common Voice) · สถานะ: **ยังไม่เริ่ม**

บรีฟงาน pilot สำหรับรันบนเครื่องผู้ใช้ (Windows, RTX 3050 Ti 4 GB) ไม่ใช่ผลทดลอง
อ่าน [`docs/RESEARCH_PROTOCOL_V2_TH.md`](../../../../docs/RESEARCH_PROTOCOL_V2_TH.md) ก่อน — สมมติฐาน ตัวแปร และค่าที่ล็อกอยู่ที่นั่น

## 1. Pilot นี้ตอบอะไร

1. G1/G2 ตัวไหนติดตั้งและรันได้จริงบนเครื่องนี้ (VRAM, เวลา)
2. อ่านภาษาไทยถูกไหม และ clone ออกมาเหมือนผู้พูดต้นแบบไหม (ผู้ใช้ฟังตัดสิน)
3. เวลา/พื้นที่สำหรับสร้างข้อมูลหลักเท่าไร
4. ดูเบื้องต้นว่าเสียง clone ใกล้สภาพเสียงจริงกว่า Wayu ไหม (ประเด็น shortcut)

ไม่ fine-tune detector ในงานนี้

## 2. Candidates

| ID | Model | ต้องตรวจ |
| --- | --- | --- |
| G1 | [`VIZINTZOR/F5-TTS-THAI`](https://huggingface.co/VIZINTZOR/F5-TTS-THAI) | license ของ fine-tune + base `SWivid/F5-TTS` แยกกัน; ฝึกจาก Common Voice Thai → บันทึก overlap risk; ต้นแบบ 2–8 วินาที + ref_text |
| G2 | [`k2-fsa/OmniVoice`](https://huggingface.co/k2-fsa/OmniVoice) | code Apache-2.0 / weights CC-BY-NC; 0.6B, 24 kHz; ยืนยันว่าอ่านไทยได้; เสี่ยง VRAM 4 GB (ลอง fp16 ก่อน CPU) |
| สำรอง G2 | Wayu (`.venv-wayu` มีแล้ว) | ถ้า G2 ไม่ผ่าน; ต้องดาวน์โหลด voice packs ที่เหลือ 11 ตัวจาก revision เดิม `8196688…` |

ไม่ใช้ ThonburianTTS คู่กับ G1 (ตระกูล F5 เดียวกัน); ใช้แทน G1 ได้ถ้า G1 ไม่ผ่าน

## 3. ข้อมูลและจริยธรรม

- ผู้ใช้อนุญาตให้ clone ผู้พูด Common Voice เพื่อการวิจัยตรวจจับ (decision log 14 ต.ค.) ยังไม่ใช่การอนุมัติของอาจารย์
- ห้าม commit/แชร์เสียงที่สร้าง เสียงต้นแบบ หรือ ID ผู้พูด; ห้ามพยายามระบุตัวตน
- ใช้เฉพาะผู้พูดใน **Train** ของ pilot_v1 (`real_train.csv`) ห้ามใช้ Dev
- `pilot_v1/` อ่านอย่างเดียว ห้ามแก้

### การเลือกคู่ข้อมูล (สำคัญ)

1. สุ่มผู้พูด 20 คนจาก `real_train.csv` ด้วย seed 42 ที่มีคลิปอื่นใน `validated.tsv` อย่างน้อย 1 คลิป ยาว 2–8 วินาที
2. **คลิปเสียงจริงที่จับคู่** = คลิปเดิมใน pilot_v1; `tts_text` = `sentence` ของคลิปนั้น
3. **คลิปต้นแบบ** = คลิปอื่นของ `client_id` เดียวกัน (ไม่ใช่คลิปที่จับคู่, ข้อความต่างกัน) เลือกด้วย seed 42; `ref_text` = `sentence` ของคลิปต้นแบบ
4. บันทึก `reference_clip_id` ทุกคลิป
5. เพิ่มคำยากคงที่ 6 ประโยค (ใช้ต้นแบบของผู้พูดคนแรก): `โม้`, `ชำระเงิน`, `โอนเงินด่วนค่ะ`, `เลขบัญชี 123-4-56789-0`, `ธนาคารกสิกรไทย`, `กรุณาติดต่อกลับภายในวันนี้`

รวม 26 คลิปต่อ generator

## 4. โครงสร้างไฟล์

| ของ | ตำแหน่ง | Git |
| --- | --- | --- |
| environment | `.venv-f5/`, `.venv-omnivoice/` | ignored |
| setup | `scripts/setup_cloning_pilot.ps1 -Generator f5\|omnivoice` (แบบ `setup_wayu_pilot.ps1`) | commit |
| requirements (pin) | `configs/cvtts/f5-pilot-requirements.txt`, `configs/cvtts/omnivoice-pilot-requirements.txt` | commit |
| สคริปต์ | `experiments/pilot/scripts/cloning/` | commit |
| weights | `checkpoints/tts/<model>/<revision>/` | ignored |
| manifest + เสียงที่สร้าง | `data/processed/cvtts/cloning_pilot_v1/` (`manifests/`, `native_tts/<generator>/`) | ignored |
| ผลวัด/รายงานดิบ | `results/pilot/cloning_feasibility/<run_id>/` | ignored |
| สรุปผล | `experiments/pilot/docs/cloning/CLONING_PILOT_RESULT_TH.md` (สถิติรวม ไม่มี ID รายคลิป) | commit |

ปรับโครงสร้างอื่นได้ถ้าจำเป็น แต่ไม่ย้าย data/ผลเก่า/pretrained, อัปเดตลิงก์ README และ pytest ต้องผ่าน (รวม `tests/pilot/test_layout.py`, `test_git_visibility.py`)

## 5. ขั้นตอน

ทำ G1 ให้จบก่อน แล้วค่อย G2 ห้ามโหลดสองโมเดลลง GPU พร้อมกัน

1. **ตรวจก่อนติดตั้ง** (หยุดให้ผู้ใช้ดู): model ID + revision, license code/weights/base, sample rate, ภาษาไทย, ขนาดดาวน์โหลด
2. **ติดตั้ง**: environment แยก, pin ทุก package, `pip check` ผ่าน, torch CUDA ที่เข้ากับไดรเวอร์
3. **เลือกคู่ข้อมูล** ตามข้อ 3 → `cloning_pilot_v1/manifests/pairs.csv`
4. **สร้างเสียง**: seed คงที่ต่อคลิป, ค่า default ของต้นทาง, ห้ามจูนพารามิเตอร์ตามผลฟัง เก็บต่อคลิป: generator, revision, reference_clip_id, ref_text, tts_text, seed, params, native sr, duration, sha256, เวลาสร้าง (แบบ `tts_wayu_train.csv`)
5. **วัดทรัพยากร**: load time, peak VRAM (`torch.cuda.max_memory_allocated` + `nvidia-smi`), RTF แยกคลิปแรก (warm-up), CPU fallback ถ้า OOM
6. **QC ฟัง**: สร้าง worksheet CSV ให้ผู้ใช้ฟังทุกคลิป: `intelligible / missing_words / wrong_words / repetition / truncation / speaker_similar(1-5) / notes` ห้ามเติมผลฟังแทนผู้ใช้
7. **สถิติสภาพเสียงเบื้องต้น**: แปลงทุกไฟล์เป็น canonical 16 kHz ด้วย `src/thai_spoof/cvtts/audio.py` แล้วเทียบ เสียงจริง / clone / Wayu (จาก pilot_v1 Train): noise floor ช่วงเงียบ (dBFS), ความถี่สูงสุดที่มีพลังงาน (-60 dB), RMS, สัดส่วนช่วงเงียบ รายงานเป็นค่าเฉลี่ย ± SD ต่อกลุ่ม
8. **ประมาณงานหลัก**: เวลาและพื้นที่สำหรับ 1,000 / 3,000 / 8,000 คลิป จาก RTF จริง
9. **รายงาน** `CLONING_PILOT_RESULT_TH.md`: ตาราง G1/G2 (ติดตั้งได้ไหม, VRAM, RTF, เวลาประมาณ, ผล QC จากผู้ใช้, สถิติข้อ 7, license, ความเสี่ยง) และข้อเสนอว่าจะใช้คู่ไหน

## 6. เกณฑ์ผ่าน

- รันจบ 26 คลิปโดยไม่ OOM (GPU หรือ CPU)
- เวลาประมาณสำหรับ 3,000 คลิป ≤ 24 ชั่วโมงบนเครื่องนี้
- ผู้ใช้ให้ intelligible ≥ 90% และ speaker_similar เฉลี่ย ≥ 3
- license ใช้งานวิชาการแบบไม่เผยแพร่เสียงได้ และบันทึกครบ

ไม่ผ่าน → บันทึกเหตุผล ไปตัวสำรอง ห้ามแก้เกณฑ์ย้อนหลัง

## 7. ห้ามทำ

- ห้าม fine-tune detector, ห้ามแก้ `pilot_v1/` หรือผล pilot เดิม
- ห้าม commit/push และห้ามใส่ attribution ของ AI ใน commit/PR — จบงานให้สรุปไฟล์ที่ควร commit; branch ที่แนะนำ `feat-cloning-pilot`
