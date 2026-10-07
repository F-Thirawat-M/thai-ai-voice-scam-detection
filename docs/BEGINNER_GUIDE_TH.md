# เริ่มใช้งาน: Common Voice + TTS + ตัวตรวจจับ

## เข้าใจบทบาทก่อน

- **Common Voice**: แหล่งเสียงมนุษย์และข้อความ; ต้องตรวจ release และสิทธิ์ของข้อมูลที่จะใช้
- **TTS**: โมเดลสร้างเสียงพูดจากข้อความ ใช้สร้างกลุ่ม spoof
- **AASIST / RawNet2**: ตัวตรวจจับเสียงจริงกับเสียงสังเคราะห์ ไม่ใช่ตัวสร้างเสียง
- **Inference**: ใช้น้ำหนักที่ฝึกแล้วทำนาย ยังไม่มีการเรียนรู้เพิ่ม
- **Fine-tuning**: ฝึกปรับน้ำหนักด้วยข้อมูลของโครงงาน
- **Train / Dev / Final Test**: ใช้ฝึก / เลือกวิธีและ threshold / ประเมินขั้นสุดท้าย ตามลำดับ

ตอนนี้มี pretrained inference และ AASIST Clean feasibility smoke 1 epoch แล้ว การรัน sample ได้ไม่เท่ากับ fine-tune สำเร็จ และการฝึกสำเร็จไม่เท่ากับตรวจแม่นขึ้น

## ขั้นล่าสุด: ลองฝึก AASIST จริงรอบสั้น

อ่าน [คู่มือ AASIST Clean smoke และผลรอบแรก](AASIST_CLEAN_SMOKE_TH.md) ใช้ `.venv` หลัก Script `scripts/train_aasist_pilot.py` ฝึก Train 160 คลิป/ตรวจ Dev 40 คลิป มี gradient, parameter update และ fresh-model checkpoint reload ผ่านแล้ว ผลใน `results/cvtts/aasist_clean_smoke/` ไม่เข้า Git ยังไม่มี RawNet2 training, Noise/Telephone, best selection, resume หรือ Final Test

Dev loss รอบแรกเพิ่มจากประมาณ 1.59 เป็น 4.85 จึงสรุปเพียงว่าฝึกได้จริง ไม่ใช่ดีขึ้น ขั้นถัดไปควรตรวจ overfit-small-batch/recipe ก่อนขยายงาน ไม่ฝึกต่อเพื่อไล่คะแนนโดยไม่มี run log

## ขั้นเตรียมเสียงร่วมก่อนลอง train

หลังมี Wayu ครบ pilot ใช้ [common_voice_pilot_audio.ipynb](../data/exploration/common_voice/common_voice_pilot_audio.ipynb) เลือก **`.venv` หลัก** เพื่อทำไฟล์ใหม่ทั้งสองคลาสเป็น WAV FLOAT mono 16 kHz โดยเก็บความยาวเต็ม ไม่ตัดเหลือ 4 วินาที ไม่เติม noise/telephone ไม่ normalize gain และไม่แก้ native data ดูผลที่รันแล้วใน `data/exploration/common_voice/outputs/` ที่ไม่เข้า Git

ใช้รายการใหม่ `wayu_pilot_train_clean16k.csv` / `wayu_pilot_dev_clean16k.csv` ภายใน `data/processed/cvtts/pilot_v1/manifests/` มี source/output hashes ย้อนตรวจได้ ขั้น canonical ไม่ฝึกโมเดล ส่วน script smoke ที่เพิ่มภายหลังเลือก window เฉพาะตอนสร้าง tensor: Train random inclusive crop / Dev first crop, คลิปสั้น repeat ให้ครบ 64,600 samples โดยไม่แก้เสียงเต็ม ไม่รายงาน EER จากขั้นเตรียมเสียง การเปลี่ยนรูปแบบไฟล์ไม่ได้ลบ artefacts/แบนด์วิดท์จากต้นทาง

## ขั้นเตรียม Wayu ครบชุดทดลองเล็ก

หลัง EDA แบ่งเสียงคนเป็น Train 80 / Dev 20 และฟัง Wayu review10 แล้ว ใช้ [notebook สร้างครบ pilot](../data/exploration/common_voice/common_voice_wayu_pilot_dataset.ipynb) เลือก `.venv-wayu` ไม่ใช่ `.venv` หลัก เครื่องใหม่เตรียม environment ด้วย `scripts/setup_wayu_pilot.ps1 -Dataset` หลังมี raw Common Voice และ manifests จาก EDA ก่อน ไม่ต้องสร้าง MMS เพื่อรัน notebook นี้

ผลคือ Wayu Train 80 / Dev 20 และรายการเสียงคน+TTS ใน `wayu_pilot_train_native.csv` (160) / `wayu_pilot_dev_native.csv` (40) ภายใน `data/processed/cvtts/pilot_v1/manifests/` ใช้ข้อความแต่ละ split ตามเดิม ไม่ใช่ Final Test ใช้ TTS ตัวเดียวเพื่อทดลอง pipeline ไม่ได้ตัดโมเดลอื่นจากแผนวิจัย

**Notebook สร้าง Wayu ไม่ใช่การ train:** เสียงคนเป็น MP3 native rate ส่วน Wayu เป็น WAV 24 kHz ใช้ canonical notebook จัดเสียงร่วมกันก่อน script smoke ไม่ใช้ CLI inference เดิมเป็นคำสั่ง fine-tune อีก 90 คลิปใหม่ผ่านได้เพียงตรวจเทคนิคจนกว่าจะฟังตรวจ ไม่เติม noise/telephone ในขั้นสร้างเสียง

## เริ่มตรวจของที่มี

เปิด PowerShell ที่ project root:

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe -m thai_spoof.cli --help
.\.venv\Scripts\python.exe -m pytest -q
```

สคริปต์ตรวจ Python/Torch/CUDA/GPU และไฟล์ AASIST; RAM/พื้นที่ว่างต้องตรวจแยก ไม่รัน setup หรืออัปเกรด package โดยไม่จำเป็น

## ทดลองทำนาย

```powershell
.\.venv\Scripts\python.exe scripts\create_smoke_audio.py
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model aasist --audio data\sample\smoke_tone.wav
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model rawnet2 --audio data\sample\smoke_tone.wav
```

เสียง smoke เป็นสัญญาณจำลอง ตรวจเพียงว่าโค้ดทำงาน ผลทายไม่บอกความแม่นยำ ใช้เสียงพูดของตนเองได้โดยเปลี่ยน path; อย่าใส่ไฟล์ส่วนตัวเข้า Git

ทั้งสองระบบปัจจุบันเตรียมเสียงเป็น mono 16 kHz ใช้ window 64,600 samples ประมาณ 4.04 วินาที ค่าเริ่มต้นใช้ช่วงแรกและวนซ้ำเมื่อสั้น ไม่ได้จำกัดว่าไฟล์ต้นทางต้องยาวเท่านี้ RawNet2 มีตัวเลือก all-chunks แต่ไม่ใช้ตัวเลือกนี้ฝ่ายเดียวในการเปรียบเทียบหลัก

## เริ่มโครงงานใหม่จากตรงไหน

1. อ่าน [workflow ส่วน 1–5](COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s01) และตกลงกับเพื่อน/อาจารย์
2. ตรวจ Common Voice ที่จะใช้ว่าเป็น release ไหน อยู่ที่ไหน และมี metadata/audio อะไรบ้าง
3. พัฒนา EDA ใน `data/exploration/common_voice/` และ helper กลางใน `src/thai_spoof/cvtts/`
4. แบ่งผู้พูด/ข้อความ/เสียงซ้ำออกจากกันก่อนสร้าง TTS
5. Pilot TTS → สร้าง corpus → Clean/Mixed → fine-tune → Dev → Final Test ตาม workflow

ยังไม่ต้องหา SEA-Spoof/Typhoon หรือรันสคริปต์ของชุดเก่า เพราะเอาออกจากขอบเขตและ repository แล้ว

ดูตำแหน่งไฟล์ใน [โครงสร้างโปรเจกต์](PROJECT_STRUCTURE_TH.md) และงานย่อย/คำสั่งที่ต้องพัฒนาที่ [workflow ส่วน 20–21](COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s20) คำสั่ง proposed ยังรันไม่ได้จนกว่าจะ implement

## ข้อควรจำ

- ไม่มีข้อมูลไม่เท่ากับไม่มี missing values: ต้องตรวจไฟล์จริงก่อนรายงาน
- Clean หมายถึงไม่เติม condition จำลอง ไม่ได้แปลว่าเสียงไม่มี noise อยู่เดิม
- Mixed ในแผน v1 คือเลือก clean หรือ noise หรือ telephone ไม่ใช่ใส่ noise+telephone พร้อมกันทุกคลิป
- Dev ใช้ปรับได้; Final Test ไม่ใช้ย้อนเลือกวิธี
- ค่า softmax ของ pretrained model ไม่ใช่ความน่าเชื่อถือในการพิสูจน์เสียงจริง/ปลอม
