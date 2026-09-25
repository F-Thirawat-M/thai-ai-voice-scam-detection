# Thai AI Voice Detection

โปรเจกต์ทดลองจำแนกเสียงพูดภาษาไทยระหว่างเสียงมนุษย์จริง (`bonafide`) และเสียงสังเคราะห์ (`spoof`) โดยเริ่มจากโมเดล AASIST ที่ผ่านการฝึกบน ASVspoof 2019

## สถานะปัจจุบัน

- มีโค้ด AASIST และ pretrained checkpoint ทางการใน `external/aasist/`
- มีคำสั่งตรวจ GPU และ dependency
- มีคำสั่ง inference สำหรับไฟล์ WAV/FLAC หนึ่งไฟล์
- มีคำสั่งประเมินไฟล์หลายรายการจาก CSV manifest
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
  --output results\baseline_scores.csv
```

รูปแบบ label ที่รองรับคือ `bonafide` และ `spoof`

### เตรียม SEA-Spoof ภาษาไทยที่ได้รับอนุญาต

เก็บข้อมูลที่ดาวน์โหลดไว้เฉพาะในเครื่องตามโครงสร้างนี้ (ไฟล์เสียงและ manifest ที่สร้างจากข้อมูลนี้ถูก `.gitignore`):

```text
data/raw/sea_spoof_th/
  thai_metadata.jsonl
  audio/evaluation/*.flac
```

ไฟล์ metadata จาก Google Drive มี `audio_path` เป็น path ของเครื่อง Colab เดิม สคริปต์ต่อไปนี้จะแปลงเป็น path ในเครื่อง ตรวจว่ามีไฟล์เสียงครบทุกแถว และสร้าง manifest เฉพาะภาษาไทยชุด `evaluation`:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_thai_manifest.py
```

ถ้าไฟล์เสียงยังไม่ครบ สคริปต์จะหยุดโดยไม่สร้าง manifest อย่าใช้ชุดที่ไม่ครบเป็นผล baseline สำหรับรายงาน เมื่อผ่านแล้วจึงรัน:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.cli evaluate `
  --manifest data\manifests\thai_evaluation.csv `
  --output results\baseline_scores.csv
```

## ลำดับการทำงานของโครงงาน

1. ทำให้ inference และ GPU ผ่าน
2. ขอสิทธิ์ SEA-Spoof และตรวจ metadata ภาษาไทย
3. สร้าง manifest โดยแยกผู้พูดระหว่าง train/validation/test
4. วัด pretrained AASIST บนเสียงไทยสะอาด
5. วัดซ้ำภายใต้ noise และ telephone codec
6. Fine-tune ด้วยข้อมูลไทยและ multi-condition augmentation
7. เพิ่ม RawNet2 เพื่อเปรียบเทียบ

อ่านคำอธิบายสำหรับผู้เริ่มต้นใน `docs/BEGINNER_GUIDE_TH.md`

## โครงสร้างสำคัญ

```text
configs/                 ค่าตั้งต้นของโมเดลและเสียง
data/manifests/          รายการไฟล์และ label
data/sample/             ไฟล์เสียงทดลองส่วนตัว (ไม่ถูกเพิ่มเข้า Git)
docs/                    คู่มือ
external/aasist/         โค้ดและ checkpoint AASIST ทางการ
results/                 คะแนนและผลการทดลอง
scripts/                 คำสั่งติดตั้งและตรวจเครื่อง
src/thai_spoof/          โค้ดของโปรเจกต์เรา
tests/                   automated tests
```

## แหล่งที่มา

- AASIST: https://github.com/clovaai/aasist
- SEA-Spoof: https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof
- PyTorch installation: https://pytorch.org/get-started/locally/
