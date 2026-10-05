# Common Voice EDA แบบง่าย

**คลิป 3 seed probe (หัวข้อ 9–10 ใน notebook TTS):** ทดลอง seed 7/123/2026 ที่กำหนดไว้ก่อนฟัง เทียบ seed 42 โดยข้อความ “ฉันไม่ได้คุยโม้” และโมเดล/ค่าการสร้างเหมือนเดิม ตรวจ tokenizer และ roundtrip ก่อนสร้าง เก็บเสียงใหม่สามแบบพร้อมรายงานชื่อลงท้าย `_seed_probe_v1_seed...` และสรุปที่ `qc/tts_experiments/clip3_seed_probe_v1.json` ไม่แทนที่ baseline ไม่เปลี่ยน manifest review10 และยังไม่เลือก seed ที่ใช้กับชุดเต็มจนฟังตรวจ ไม่ใช้ผล detector เลือกเสียง

**MMS Thai text-preparation fix (หัวข้อ 7–8 ใน notebook TTS):** ตรวจพบว่า tokenizer ที่ pin ไว้ไม่รองรับ U+0E33 (`ำ`) และตัดออกก่อน encode จึงทดลองใช้รูป U+0E4D + U+0E32 (`ํ` + `า`) เฉพาะคลิป 10 พร้อมตรวจข้อความหลัง tokenizer และ token roundtrip ใช้ helper `thai_spoof.cvtts.text` ที่มี tests บันทึกข้อความเดิม/ข้อความเข้า TTS/normalization version และเสียงใหม่ชื่อ `_sara_am_v1_seed42` แยกจาก baseline 10 คลิป ไม่แก้ manifest เดิม ไม่เปลี่ยนคลิป 3 และยังรอฟังตรวจ หัวข้อ 1–6 คงไว้เพื่อเทียบ baseline ที่มีข้อผิดพลาด ห้ามนำไปสร้างชุดเต็มโดยไม่ใช้ policy ที่ตรวจแล้ว

**ขั้นที่ 4 (แยกจาก EDA):** เปิด [common_voice_tts_pilot.ipynb](common_voice_tts_pilot.ipynb) เพื่ออ่านข้อความจาก Train และใช้ MMS Thai ที่ล็อก revision สร้างเสียงสังเคราะห์เพียง 1 คลิป รันใน `.venv` บน CPU; optional dependencies อยู่ใน `.[tts]` โมเดลดาวน์โหลดครั้งแรกประมาณ 145 MB และอยู่ `checkpoints/tts/` ไม่โหลด remote code/weights pickle ไม่ส่งเสียงคนให้ API และไม่ทำ voice cloning ไฟล์เสียงอยู่ `data/processed/cvtts/pilot_v1/native_tts/mms_tha/train/` พร้อม JSON ที่ `qc/tts_samples/` ต้องฟังตรวจเองก่อนสร้างเพิ่ม (status `pending`) ไม่ถือว่าชุดสองคลาสพร้อม train แล้ว ผลที่รันแล้วเก็บใน [outputs/common_voice_tts_pilot.executed.ipynb](outputs/common_voice_tts_pilot.executed.ipynb) โมเดลมีข้อจำกัด CC-BY-NC 4.0 ตาม [model card](https://huggingface.co/facebook/mms-tts-tha)

เปิด [common_voice_eda.ipynb](common_voice_eda.ipynb) ใน VS Code เลือก **Select Kernel → Python Environments → .venv** แล้วกด **Run All** หรือรันทีละเซลล์จากบนลงล่าง เริ่มด้วย `pd.read_csv()`, `df.head()`, `df.shape`, `df.info()` และ `df.columns`

**TTS review batch:** หัวข้อ 5–6 ของ `common_voice_tts_pilot.ipynb` เพิ่มตัวอย่าง Train ให้ครบ 10 คลิป รวมคลิปแรกและอีก 9 ข้อความที่กระจายตามความยาวข้อความ ใช้โมเดล/การตั้งค่า/seed เดิม ตรวจ hash ก่อนใช้ไฟล์ที่มีแล้ว ไม่ใช้ Dev และไม่สร้างครบ 100 คลิป รายการอยู่ `data/processed/cvtts/pilot_v1/manifests/tts_train_review10.csv` ผลฟังจริงจากผู้ใช้เก็บแยกใน `qc/tts_reviews/` เพื่อไม่แก้ provenance เดิม; อีก 9 คลิปยังรอฟังตรวจ มี player ทีละข้อท้าย notebook

สิ่งที่ดูได้: ไฟล์ TSV ทั้งแพ็กและบทบาท, จำนวนคลิป, 13 คอลัมน์ต้นทาง, ค่าว่าง, ชื่อไฟล์/ข้อความซ้ำ, ความยาวเสียงและคลิปที่เกิน 4.04/6/8 วินาที, อายุ/เพศ/สำเนียง, speaker keys, โหวต, ข้อความ, ไฟล์เสียงที่มีจริง และ sample rate/channels ของตัวอย่าง 5 คลิป พร้อมฟังตัวอย่างหนึ่งคลิป

ใช้ pandas ตรงใน notebook ไม่ต้องเรียก helper หรือ CLI ใหม่ ข้อมูลดิบที่ใช้คือ `data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/` ส่วนผลที่รันแล้วอยู่ [outputs/common_voice_eda.executed.ipynb](outputs/common_voice_eda.executed.ipynb) ในเครื่องนี้และไม่เข้า Git

`df` คือ validated; `df_all` รวม validated/invalidated/other เท่านั้น Train/Dev/Test ต้นทางเป็นส่วนย่อยจึงไม่บวกซ้ำ คอลัมน์ `clip_status`/`duration_s` เป็นสิ่งที่เติมเองเพื่อดูข้อมูล ไม่ใช่ฟีเจอร์ต้นทางหรือ input โมเดล

ความยาวในส่วน EDA อ่านจาก metadata ไม่ใช่ decode ทุกไฟล์; ขั้นเตรียมทดลอง 2 อ่านเสียงเต็มเฉพาะชุด 100 คลิป จำนวน client_id คือรหัสผู้พูดไม่ซ้ำในต้นทาง ยังไม่ยืนยันจำนวนบุคคลจริง Notebook ไม่แก้ raw data ไม่สร้าง TTS และไม่ train

ท้าย notebook มี **ขั้นเตรียมทดลอง 1**: สร้าง `df_candidates` จาก validated โดยเก็บเฉพาะแถวที่ `client_id`, `path`, `sentence` ไม่ว่าง พร้อมนับจำนวนก่อน/หลังคัด

**ขั้นเตรียมทดลอง 2**: สร้าง `df_pilot` ชุดเล็ก 100 คลิปด้วย seed 42 เลือกหนึ่งคลิปต่อรหัสผู้พูดและไม่ซ้ำข้อความหลัง Unicode/whitespace normalization อ่านเสียงเต็มคลิป ตรวจเสียงว่าง/NaN/infinity/เงียบเกือบศูนย์ และ hash เสียงที่ decode แล้วว่าซ้ำกันภายในชุดนี้หรือไม่ หากมีปัญหาจะหยุด ไม่ลบหรือข้ามไฟล์อัตโนมัติ มีเซลล์ฟังตัวอย่างจากชุดนี้ด้วย นี่เป็น pilot เพื่อเช็กกระบวนการ ไม่ใช่ Final Test หรือชุดสำหรับสรุปผลวิจัย ยังไม่แบ่ง Train/Dev ไม่แปลงเสียงและไม่สร้าง TTS การตรวจเสียงซ้ำครอบคลุมเฉพาะ 100 คลิป ไม่ใช่ทั้ง corpus

ก่อน commit notebook ต้นแบบให้ clear outputs; เก็บไฟล์ที่มีผลจริงใน `outputs/` แผนงานฉบับละเอียดอยู่ใน [workflow Phase 1](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s08)

**ขั้นเตรียมทดลอง 3**: แบ่งชุด pilot เป็น Train 80 / Dev 20 ด้วย seed 43 และตรวจรหัสผู้พูด ข้อความที่ normalize ชื่อไฟล์ decoded PCM hash และ file hash ว่าไม่มีรายการร่วมกันข้ามชุด บันทึก `real_all.csv`, `real_train.csv`, `real_dev.csv` ใน `data/processed/cvtts/pilot_v1/manifests/` และ `pilot_split_report.json` ใน `qc/` พร้อม seeds, source metadata hash และ manifest hashes รันซ้ำได้เมื่อข้อมูลตรงเดิม แต่จะหยุดถ้าผลต่างจากไฟล์ version เดิม

รายการที่บันทึกยังเป็น MP3 native sample rate และมีเฉพาะ label `bonafide` ไม่ใช่ข้อมูลที่พร้อม train สองคลาสหรือ manifest สำหรับสั่ง CLI เดิมทันที `audio_path` เป็น path จาก project root; `path` คือชื่อไฟล์ต้นทาง ไม่คัดลอกเสียง 100 ไฟล์ เมื่อสร้าง TTS ต้องให้เสียงปลอมสืบทอด split จากข้อความต้นทาง ชุดนี้ไม่มี Final Test และไม่ใช้รายงานประสิทธิภาพสุดท้าย รหัสผู้พูด/ข้อความ/เสียงของ pilot ต้องกันออกจาก Final Test ที่จัดภายหลังด้วย
