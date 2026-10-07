# Thai Synthetic Speech Detection

โครงงานเปรียบเทียบ **AASIST และ RawNet2** สำหรับตรวจเสียงสังเคราะห์ภาษาไทย โดยใช้ Common Voice เป็นแหล่งเสียงจริง/ข้อความ และสร้างเสียงปลอมด้วย TTS หลายระบบ เปรียบเทียบการ fine-tune แบบ Clean กับ Clean + Noise + Telephone

## เริ่มอ่าน

- [Workflow ทั้งโปรเจกต์](docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md): ขั้นตอนละเอียด ข้อตกลงการทดลอง และ prompt ส่งต่อให้ AI
- [โครงสร้างและตำแหน่งเก็บไฟล์](docs/PROJECT_STRUCTURE_TH.md): อะไรมีแล้ว และอะไรต้องพัฒนาต่อ
- [เริ่มใช้งานสำหรับผู้เริ่มต้น](docs/BEGINNER_GUIDE_TH.md): ตรวจเครื่องและทดลอง inference ที่มีอยู่
- [AASIST Clean smoke 1 epoch](docs/AASIST_CLEAN_SMOKE_TH.md): วิธีฝึกรอบสั้น ผลครั้งแรก และข้อจำกัด
- [ทดลองจำ Train 4 คลิป](docs/AASIST_OVERFIT_CHECK_TH.md): diagnostic ผ่านแล้ว; ไม่ใช่ความแม่นยำกับเสียงใหม่
- [การจัดการข้อมูล](data/README.md): raw / processed / exploration / sample
- [Common Voice EDA แบบง่าย](data/exploration/common_voice/common_voice_eda.ipynb): เริ่มดู df, คอลัมน์, ค่าว่าง, ความยาวเสียง และผู้พูด
- [รายการทำความสะอาด](docs/CLEANUP_2026-10-03.md): สิ่งที่ลบและข้อจำกัดการกู้คืน

## สถานะจริง

มี pretrained inference ของ AASIST/RawNet2, CLI `infer/evaluate`, checkpoint, environment check และ tests พื้นฐานแล้ว

มี notebooks EDA/split/pilot synthesis ของ Common Voice และ shared canonical audio พร้อม AASIST **Clean feasibility smoke 1 epoch** ที่มีการอัปเดตน้ำหนักและตรวจ reload จริงแล้ว ผลนี้ยังไม่ใช่ความสำเร็จด้านความแม่นยำ (Dev loss รอบแรกสูงขึ้น) และมี Wayu generator เดียว

เพิ่ม fixed-Train-subset memorization check: จำคน 2 + Wayu 2 ได้หลัง 20 updates (subset loss 0.002260 / accuracy 100% บนคลิปที่ฝึกซ้ำ) ไม่ใช้ Dev/Test และไม่บอกสาเหตุ Dev loss เดิม ยังอยู่ใน pilot

**ยังไม่มี** automated full-corpus pipeline, multi-condition/main-run training, RawNet2 fine-tuning หรือ Final Test แบบ fixed Dev threshold ไม่ได้หมายความว่าการทดลองวิจัยเสร็จแล้ว

SEA-Spoof/Typhoon พร้อม pipeline และเอกสารแผนเดิมถูกนำออกตามการปรับขอบเขต ไม่ต้องโหลดชุดเหล่านั้นเพื่อเริ่มงานใหม่

## โครงสร้างหลัก

```text
configs/cvtts/              ที่เก็บ protocol และ TTS/run configs ที่จะสร้าง
data/
  raw/common_voice/        ชุดต้นทาง; เครื่องนี้มี Common Voice Thai 27.0 แล้ว
  raw/noise/               noise recordings ต้นทาง
  processed/cvtts/         corpus ที่สร้างและ versioned manifests
  exploration/common_voice/  notebook EDA แบบง่ายและผลเฉพาะเครื่อง
  sample/                 เสียงทดลอง inference ไม่ใช่ train/test
docs/                     คู่มือ, workflow, decisions, reports
examples/                 ตัวอย่างสังเคราะห์/placeholder ที่ commit ได้
src/thai_spoof/
  aasist/                 adapter/config/preprocessing ของ AASIST ที่มีแล้ว
  rawnet2/                adapter/model/config ของ RawNet2 ที่มีแล้ว
  cvtts/                  พื้นที่ pipeline ข้อมูล/ฝึกใหม่ (ยังเป็น scaffold)
  cli.py                  คำสั่ง inference ร่วม
  metrics.py              legacy metrics; ต้องพัฒนาก่อนใช้ Final Test
  prediction.py           รูปแบบผลทำนายร่วม
scripts/                  setup, environment check, smoke signal
tests/                    tests ที่ใช้อยู่ และตำแหน่ง tests/cvtts สำหรับงานใหม่
external/aasist/           upstream source ที่ inference ยังใช้งาน
checkpoints/              pretrained weights และน้ำหนักที่จะ fine-tune
results/                  ผลที่สร้างในเครื่อง ไม่ commit
tmp/                      ไฟล์ชั่วคราวที่สร้างใหม่ได้
```

ข้อมูลหลักใช้ร่วมกันทั้งสองโมเดล ไม่ทำสำเนา dataset แยกตาม model; แยก model/arm/seed ที่ run config, checkpoint และผลทดลอง

## ตรวจเครื่องและทดลองสิ่งที่มีแล้ว

เปิด PowerShell ที่ project root:

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe -m thai_spoof.cli --help
.\.venv\Scripts\python.exe scripts\create_smoke_audio.py
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model aasist --audio data\sample\smoke_tone.wav
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model rawnet2 --audio data\sample\smoke_tone.wav
.\.venv\Scripts\python.exe -m pytest -q
```

Smoke signal ไม่ใช่เสียงพูด ผลทายไม่มีความหมายทางวิจัย สำหรับเสียงพูดของตนเองให้วาง WAV/FLAC ใน `data/sample/` แล้วเปลี่ยน path

เครื่องใหม่อ่าน `scripts/setup.ps1` ก่อนรัน เพราะติดตั้ง dependencies/ดาวน์โหลด upstream; เครื่องนี้ไม่ต้องรัน setup ซ้ำเพื่อปรับโครงสร้าง ถ้าขาด RawNet2 weights จึงใช้ `python -m thai_spoof.rawnet2.setup_checkpoint`

## ประเมินหลายไฟล์ด้วย CLI เดิม

ตัวอย่างคอลัมน์อยู่ที่ [examples/inference_manifest.csv](examples/inference_manifest.csv) เป็นชื่อไฟล์สมมติ ไม่ใช่ข้อมูลพร้อมรัน ให้สร้าง manifest จริงใน `data/processed/cvtts/<version>/manifests/` หรือพื้นที่ส่วนตัวที่ไม่ commit

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.cli evaluate --model aasist --manifest path\to\your_manifest.csv --output results\manual\aasist_scores.csv
```

Relative audio paths ใน CLI เดิมอ้างจาก working directory; labels คือ `bonafide/spoof` คะแนน AASIST/RawNet2 ยังคนละสเกลและยังไม่ calibrated สำหรับไทย **metrics เดิมเลือก threshold จากชุดที่ส่งเข้าไป จึงห้ามใช้ accuracy/confusion จาก Final Test เป็นผลตาม protocol ใหม่** จนพัฒนาส่วน Dev threshold แยกแล้ว

## งานถัดไป

ตรวจจำชุดเล็กผ่านแล้ว ขั้นต่อไปคือเช็ก recipe ด้วย Train/Dev แบบเปลี่ยนทีละปัจจัย ก่อนเพิ่ม TTS ระบบที่สองและพัฒนา Noise/Telephone, resume, Dev selection/threshold สำหรับ main runs โดยยังต้องยืนยัน scope/สิทธิ์ตาม workflow ดู [ผลและขั้นต่อไป](docs/AASIST_OVERFIT_CHECK_TH.md)

Branch ใช้ชื่อตาม feature โดยไม่ใส่ `codex/`; ผู้ใช้เป็นผู้ commit/push เอง

## ที่มาโมเดล

- [AASIST ทางการ](https://github.com/clovaai/aasist)
- [RawNet2 integration ต้นทาง](https://github.com/Nattadol/thai-audio-deepfake)
- [ASVspoof 2021 baselines](https://github.com/asvspoof-challenge/2021)

เก็บ attribution/license ของโค้ดทั้งสองโมเดลไว้เหมือนเดิม รายละเอียดใน [AASIST](src/thai_spoof/aasist/README.md) และ [RawNet2](src/thai_spoof/rawnet2/README.md)
