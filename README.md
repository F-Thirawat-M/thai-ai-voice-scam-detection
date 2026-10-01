# Thai AI Voice Detection

โปรเจกต์ทดลองจำแนกเสียงพูดภาษาไทยระหว่างเสียงมนุษย์จริง (`bonafide`) และเสียงสังเคราะห์ (`spoof`) โดยเริ่มจากโมเดล AASIST ที่ผ่านการฝึกบน ASVspoof 2019

## สถานะปัจจุบัน

- มีโค้ด AASIST ทางการใน `external/aasist/` และน้ำหนักใน `checkpoints/aasist/`
- มีคำสั่งตรวจ GPU และ dependency
- มีคำสั่ง inference สำหรับไฟล์ WAV/FLAC หนึ่งไฟล์
- มีคำสั่งประเมินไฟล์หลายรายการจาก CSV manifest
- เลือก AASIST หรือ RawNet2 baseline ผ่าน `--model` ได้
- ยังไม่ได้ fine-tune ด้วยภาษาไทย ดังนั้นผลรายไฟล์ในช่วงนี้เป็น baseline เพื่อการวิจัย ไม่ใช่เครื่องมือตัดสินเสียงปลอมจริง

## เริ่มใช้งาน

เปิด PowerShell ที่โฟลเดอร์นี้ แล้วรัน:

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\check_environment.py
```

หากทุกอย่างถูกต้อง บรรทัด `CUDA available` ควรเป็น `True`

ทดสอบเส้นทางโปรแกรมทั้งหมดด้วยสัญญาณจำลอง (ผลการจำแนกไม่มีความหมายทางวิจัย):

```powershell
.\.venv\Scripts\python.exe scripts\create_smoke_audio.py
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --audio data\sample\smoke_tone.wav
```

### ตรวจเสียงหนึ่งไฟล์

วางไฟล์ WAV หรือ FLAC ใน `data/sample/` แล้วรัน:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --audio data\sample\your_voice.wav
```

ค่าเริ่มต้นใช้ AASIST และสามารถระบุโมเดลให้ชัดเจนด้วย `--model aasist` ได้

### ทดลอง RawNet2

ติดตั้ง checkpoint ทางการครั้งแรก (ประมาณ 66 MB; ไฟล์จะอยู่ใน `checkpoints/` และไม่ถูกเพิ่มเข้า Git):

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.rawnet2.setup_checkpoint
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model rawnet2 --audio data\sample\your_voice.wav
```

ค่าเริ่มต้นตรวจช่วงแรกประมาณ 4.04 วินาที หากต้องการเฉลี่ยคะแนนทุกช่วงของไฟล์ ใช้ `--all-chunks` กับ RawNet2 คะแนนที่พิมพ์ออกมาไม่ได้ผ่านการ calibration สำหรับภาษาไทย

ผลตัวอย่าง:

```text
device: cuda
prediction: bonafide
bonafide_probability: 0.812345
spoof_probability: 0.187655
```

ค่าความน่าจะเป็นนี้ไม่ได้ผ่านการ calibration และ pretrained model ยังไม่เคย fine-tune ด้วยภาษาไทย จึงห้ามตีความเป็นความน่าเชื่อถือทางนิติวิทยาศาสตร์

### ประเมินหลายไฟล์

คัดลอก `data/manifests/example.csv` แล้วแก้ `path` และ `label` ให้ตรงกับข้อมูลจริง:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.cli evaluate `
  --manifest data\manifests\example.csv `
  --model aasist `
  --output results\aasist\baseline_scores.csv
```

รูปแบบ label ที่รองรับคือ `bonafide` และ `spoof`
สามารถเปลี่ยนเป็น `--model rawnet2` และใช้ `--output results\rawnet2\baseline_scores.csv` เพื่อเทียบผลสองโมเดลบน manifest เดียวกัน CSV ผลลัพธ์มี `model`, `score_type` และ `segments` กำกับ AASIST ใช้ logit ส่วน RawNet2 ใช้ softmax score จึงไม่ควรเทียบค่าคะแนนดิบข้ามโมเดลโดยตรง

### เตรียม SEA-Spoof ภาษาไทยที่ได้รับอนุญาต

ใช้ split เดิมของ SEA-Spoof เสมอ: `train` สำหรับฝึก, `validation` สำหรับเลือก checkpoint/threshold, `evaluation` สำหรับวัดผลตามแผนที่กำหนดไว้ ห้ามสุ่มแบ่งใหม่ ข้อมูลที่ดาวน์โหลดและไฟล์ที่สกัดได้ถูก `.gitignore` และไม่ควรแชร์กับผู้ที่ไม่ได้รับสิทธิ์

วาง Parquet จาก Hugging Face ไว้ที่ `data/raw/sea_spoof_hf/data/<split>/*.parquet` แล้วติดตั้ง dependency สำหรับการสกัดข้อมูล:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[data]"
```

สกัดเฉพาะภาษาไทยจาก Dev และ Test โดยไม่แก้ Parquet ต้นฉบับ:

```powershell
.\.venv\Scripts\python.exe scripts\extract_thai_parquet.py --split validation
.\.venv\Scripts\python.exe scripts\extract_thai_parquet.py --split evaluation
```

ผลอยู่ที่ `data/processed/sea_spoof_th/audio/<split>/*.flac` และ `data/manifests/thai_dev.csv`, `data/manifests/thai_test.csv` แต่ละ manifest เก็บ `path`, `row_id`, `label`, `language`, `split` และ metadata ทุกคอลัมน์จากต้นทาง ยกเว้น audio bytes ที่บันทึกเป็น FLAC แยกไว้ สคริปต์ตรวจ FLAC, sample rate, label และ `row_id` ซ้ำก่อนสร้าง manifest ฉบับสมบูรณ์ รันซ้ำได้โดยไม่ทับเสียงที่ต่างจากต้นทาง

ขั้นต่อไปคือรัน pretrained ทั้งสองโมเดลบน manifest เดียวกัน โดยเลือก threshold จาก Dev เท่านั้น อย่าใช้ Test เพื่อเลือก threshold หรือปรับโมเดล คำสั่ง `evaluate` ปัจจุบันคำนวณ threshold จากไฟล์ที่ส่งเข้ามา จึงยังไม่ควรใช้ค่า accuracy/confusion matrix ที่มันพิมพ์จาก Test เป็นผลวิจัยก่อนแก้ขั้น metrics นี้

เลิกใช้เส้นทางเตรียมข้อมูลจาก Google Drive แล้ว การเตรียมข้อมูลปัจจุบันใช้ `scripts/extract_thai_parquet.py` กับ Parquet จาก Hugging Face ตามคำสั่งด้านบนเท่านั้น

## ลำดับการทำงานของโครงงาน

1. ทำให้ inference และ GPU ผ่าน
2. ขอสิทธิ์ SEA-Spoof และตรวจ metadata ภาษาไทย
3. กรองภาษาไทยตาม split เดิมและสร้าง manifest โดยไม่สุ่มแบ่งใหม่
4. วัด pretrained AASIST บนเสียงไทยสะอาด
5. วัดซ้ำภายใต้ noise และ telephone codec
6. Fine-tune ด้วยข้อมูลไทยและ multi-condition augmentation
7. เปรียบเทียบ AASIST กับ RawNet2 บน manifest และเงื่อนไขการทดสอบเดียวกัน

อ่านคำอธิบายสำหรับผู้เริ่มต้นใน `docs/BEGINNER_GUIDE_TH.md`

อ่าน [แผนขอบเขต ข้อมูลประชากร และ workflow การทดลอง](docs/RESEARCH_PLAN_TH.md) ซึ่งรวมผลตรวจ metadata ของ Typhoon Isan และข้อจำกัดที่ต้องคุยกับอาจารย์ก่อนเลือกชุดเสริม

## โครงสร้างสำคัญ

สำรวจข้อมูลแบบ data science แยกตาม dataset ใน [โฟลเดอร์ EDA](data/exploration/README.md) เริ่มจาก [SEA-Spoof notebook](data/exploration/sea_spoof/sea_spoof_eda.ipynb) และอ่าน [วิธีรันกับขอบเขตการสำรวจ](data/exploration/sea_spoof/README.md) ผลที่รันแล้วเก็บใน `data/exploration/<dataset>/outputs/` ซึ่งไม่เข้า Git

```text
src/thai_spoof/
  cli.py                 คำสั่ง infer/evaluate และตัวเลือกโมเดลร่วมกัน
  prediction.py          รูปแบบผลลัพธ์ร่วมกัน
  metrics.py             การวัดผลร่วมกัน
  aasist/                ฝั่ง F-Thirawat-M: detector.py, audio.py, config.json
  rawnet2/               ฝั่ง Nattadol: detector.py, model.py, config.yaml,
                         download_checkpoint.py, setup_checkpoint.py, LICENSE
data/raw/                ข้อมูลต้นฉบับในเครื่อง
data/processed/          เสียงที่สกัดจากข้อมูลต้นฉบับ
data/manifests/          รายการไฟล์และ label
data/sample/             ไฟล์เสียงทดลองส่วนตัว
checkpoints/aasist/      น้ำหนัก AASIST
checkpoints/rawnet2/     น้ำหนัก RawNet2
external/aasist/         โค้ดเครือข่าย AASIST ทางการ
results/aasist/          ผลทดลอง AASIST
results/rawnet2/         ผลทดลอง RawNet2
scripts/                 ติดตั้งเครื่องและเตรียม dataset
docs/                    คู่มือและแผนวิจัย
tests/                   automated tests
```

งานโมเดลของแต่ละฝั่งแก้ในโฟลเดอร์ของตัวเองได้ ส่วน CLI, metrics และ dataset ใช้ร่วมกัน
อ่านคู่มือแต่ละโมเดลใน [AASIST](src/thai_spoof/aasist/README.md) และ [RawNet2](src/thai_spoof/rawnet2/README.md)
ไฟล์เสียง น้ำหนัก และผลทดลองที่สร้างในเครื่องไม่ถูกเพิ่มเข้า Git

## แหล่งที่มา

- AASIST: https://github.com/clovaai/aasist
- RawNet2 integration: https://github.com/Nattadol/thai-audio-deepfake
- RawNet2 baseline: https://www.asvspoof.org/asvspoof2021/
- SEA-Spoof: https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof
- PyTorch installation: https://pytorch.org/get-started/locally/
