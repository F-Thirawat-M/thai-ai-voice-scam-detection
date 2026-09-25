# RawNet2 baseline ที่พร้อมรัน

โฟลเดอร์นี้นำโครงสร้างโมเดลจาก ASVspoof 2021 `LA/Baseline-RawNet2` มาใช้คู่กับ checkpoint ทางการที่ฝึกด้วย ASVspoof 2019 LA แล้ว จึงไม่ใช่โมเดลน้ำหนักสุ่มเหมือนโค้ดใน `rawnet2-antispoofing` ที่ยังไม่ได้ระบุ `--model_path`

## ทดลองกับไฟล์เสียงหนึ่งไฟล์

```bash
cd "/Users/draft/Desktop/python/CS3/SEMINAR PROJECT/rawnet2-baseline-ready"
./run.sh /path/to/audio.wav
```

ตัวอย่างที่เตรียมไว้:

```bash
./run.sh examples/sample.wav
```

อินพุต WAV/FLAC จะถูกแปลงเป็น mono 16 kHz และทำ repeat-padding/cropping เป็น 64,600 samples ตาม baseline ทางการ โดยค่าเริ่มต้นใช้ช่วงแรกประมาณ 4.04 วินาที ถ้าต้องการทดสอบทั้งไฟล์และเฉลี่ยคะแนนทุกช่วง:

```bash
./run.sh --all-chunks /path/to/audio.wav
```

ผลลัพธ์ `bonafide_score` คือคะแนนคลาสเสียงจริง (class 1) และ `spoof_score` คือคะแนนคลาสเสียงปลอม (class 0) ค่าเหล่านี้เป็น softmax score ของ baseline ไม่ใช่ความน่าจะเป็นที่ผ่านการ calibrate สำหรับภาษาไทย

## เตรียม checkpoint ใหม่หากไฟล์หาย

```bash
./setup_checkpoint.sh
```

สคริปต์จะดาวน์โหลด `pre_trained_DF_RawNet2.zip` จากเว็บไซต์ ASVspoof ทางการ แตกไฟล์ และวาง checkpoint ไว้ใน `checkpoints/`

## ใช้เป็น baseline ในงานวิจัย

- โมเดลนี้ฝึกจาก ASVspoof 2019 LA ซึ่งส่วนใหญ่เป็นภาษาอังกฤษ จึงเหมาะเป็น **zero-shot baseline** สำหรับชุดเสียงภาษาไทย ไม่ควรสรุปว่าใช้งานจริงได้จาก score รายไฟล์
- รายงานผลแยก clean และ telephone-channel/noise condition ด้วย EER ก่อนเลือก threshold จาก validation set เท่านั้น
- เก็บ baseline เดิมไว้โดยไม่ fine-tune แล้วสร้างโมเดลอีกสำเนาสำหรับ fine-tune ด้วยข้อมูลภาษาไทย เพื่อให้การเปรียบเทียบยุติธรรม
- เวลาประเมิน dataset จำนวนมาก ควรเก็บ raw score ของทุกไฟล์และคำนวณ EER จาก label จริง แทนการนับผลจาก threshold 0.5

## Python environment

`run.sh` ใช้ environment ที่มีอยู่แล้วที่ `/Users/draft/Desktop/python/.venv/bin/python` ซึ่งมี PyTorch, torchaudio, soundfile และ PyYAML พร้อม หากต้องการใช้ Python ตัวอื่น ให้กำหนดตัวแปร `RAWNET2_PYTHON`:

```bash
RAWNET2_PYTHON=/path/to/python ./run.sh examples/sample.wav
```
