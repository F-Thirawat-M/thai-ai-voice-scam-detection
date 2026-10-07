# PILOT — เปิดหน้านี้เพื่อทำงานต่อ

**นี่คือทดลองเบื้องต้น ไม่ใช่ผลวิจัยหลัก** จุดประสงค์คือสร้างข้อมูลเล็ก ตรวจ TTS/audio และเช็กว่า AASIST ฝึก/เรียนรู้ได้ก่อนขยายงาน

## ถึงขั้นไหนแล้ว

| ขั้น | เปิดอะไร | สถานะ |
| --- | --- | --- |
| 1. สำรวจ Common Voice + เลือกคน 100 คลิป | [EDA notebook](notebooks/common_voice_eda.ipynb) | ทำแล้ว; Train 80 / Dev 20 |
| 2. ลอง MMS Thai | [MMS notebook](notebooks/common_voice_tts_pilot.ipynb) | ทำแล้ว; บางคำอ่านผิด ไม่ได้เป็น generator หลักของ pilot ปัจจุบัน |
| 3. ลอง Wayu และฟังตัวอย่าง | [Wayu review notebook](notebooks/common_voice_wayu_tts_pilot.ipynb) | ทำแล้ว |
| 4. สร้าง Wayu ครบชุดเล็ก | [Wayu dataset notebook](notebooks/common_voice_wayu_pilot_dataset.ipynb) | ทำแล้ว; spoof Train 80 / Dev 20 |
| 5. จัดคน+AI เป็น WAV mono 16 kHz | [Canonical notebook](notebooks/common_voice_pilot_audio.ipynb) | ทำแล้ว; 200 คลิปเต็มความยาว |
| 6. ลอง fine-tune Clean 1 epoch | [คู่มือและผล](docs/aasist/AASIST_CLEAN_SMOKE_TH.md) / [script](scripts/aasist/train_aasist_clean.py) | ทำแล้ว; Dev loss 1.59 → 4.85 (แย่ลง) |
| 7. ตรวจจำ Train 4 คลิป | [คู่มือและผล](docs/aasist/AASIST_OVERFIT_CHECK_TH.md) / [script](scripts/aasist/check_aasist_overfit.py) | ผ่าน 20 updates; 100% บนคลิปที่ฝึกซ้ำ ไม่ใช่เสียงใหม่ |
| 8. ตรวจวิธีฝึกด้วย Train/Dev | ยังต้องพัฒนา diagnostic เปลี่ยนทีละปัจจัย | **ขั้นถัดไป ยังไม่ทำ** |

**ไม่ต้องรันขั้น 1–7 ใหม่ทั้งหมด** เปิดคู่มือของขั้น 7 เพื่อเข้าใจผลล่าสุด แล้วค่อยเริ่มขั้น 8 ไม่ใช้ checkpoint ที่จำ 4 คลิปไปเป็น main model และยังไม่ไป Final Test

## แยกชนิดไฟล์ให้เข้าใจ

- `notebooks/`: เปิดใน VS Code เพื่อดูข้อมูล/สร้าง TTS/เตรียมเสียง เลือก kernel ให้ตรงขั้น
- `notebooks/outputs/`: สำเนาที่รันแล้ว มีตารางและเสียงให้ฟัง ไม่เข้า Git
- `scripts/aasist/`: คำสั่งลองฝึก AASIST ฝั่งผู้ทำ AASIST ไม่ใช่ TTS ไม่ใช่ main-run trainer
- `scripts/rawnet2/`: พื้นที่คำสั่ง RawNet2 ฝั่งเพื่อน ตอนนี้มี README ยังไม่มี trainer
- `docs/aasist/`, `docs/rawnet2/`: คู่มือแยกโมเดล ส่วนเอกสาร notebook/การย้ายไฟล์ยังใช้ร่วมกัน
- `../../src/thai_spoof/pilot/`: Dataset และฟังก์ชัน diagnostic ที่ scripts เรียก ไม่ต้องเปิดแก้เองเพื่อเริ่มอ่าน

## ของจริงในเครื่องอยู่ที่ไหน

| ของ | ตำแหน่งจาก project root |
| --- | --- |
| เสียงและรายการข้อมูล pilot | `data/processed/cvtts/pilot_v1/` |
| ผล Clean 1 epoch | `results/pilot/aasist_clean_smoke/clean_epoch1_20261007_v1/` |
| ผลจำ 4 คลิป | `results/pilot/aasist_overfit_check/fixed4_20261007_v1/` |
| น้ำหนักเริ่มต้น | `checkpoints/aasist/AASIST.pth` |

`last.pt` ภายในแต่ละ run คือ weights ของรอบนั้น ไม่ใช่ pretrained เดิม และ CLI infer เดิมไม่ได้เลือก weights นี้อัตโนมัติ

## คำสั่งที่เปลี่ยนตำแหน่งแล้ว

รันจาก **project root** ด้วย `.venv` หลัก ไม่ใช่ `.venv-wayu`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# เฉพาะเมื่อจะลองรันใหม่ภายหลัง: ต้องใช้ run-id ใหม่
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\train_aasist_clean.py --run-id my_clean_01 --device cuda
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\check_aasist_overfit.py --run-id my_overfit_01 --device cuda
```

**ไม่ต้องรันสองคำสั่งฝึกตอนนี้** ผลเดิมมีอยู่แล้ว และคำสั่งเก่าใน `scripts/` ถูกย้าย ไม่สร้าง wrapper ซ้ำให้สับสน

## เพื่อน pull แล้วเห็นอะไร

Git เก็บโค้ด คู่มือ และ `.gitkeep` ซึ่งเป็นไฟล์ว่างบอกตำแหน่งโฟลเดอร์ ไม่ได้เก็บเสียง/CSV จริง/weights/ผลฝึก ดู [คู่มือรับข้อมูลและแบ่งงาน](../../docs/TEAM_HANDOFF_TH.md) ใช้ dataset ร่วมกัน ไม่คัดลอกเป็นชุด AASIST/RawNet2 แยกกัน

## สิ่งที่ยังไม่อยู่ใน pilot นี้

ยังไม่มี TTS ตัวที่สองใน detector training corpus, Noise/Telephone training, RawNet2 fine-tuning, resume/main-run selection, Final Test หรือ EER ตาม protocol ใหม่ ดู [research/](../research/README.md) สำหรับงานวิจัยหลักและ [การย้ายไฟล์](docs/PATH_MIGRATION_TH.md) ถ้าลิงก์ที่เคยเปิดอยู่หาไม่เจอ
