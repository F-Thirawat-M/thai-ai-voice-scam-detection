# Pilot notebook — รายละเอียดเพิ่มเติม (ไม่ใช่หน้าเริ่มต้น)

## ขั้นล่าสุด: ตรวจจำ Train 4 คลิป

ทำ [fixed-input memorization check](aasist/AASIST_OVERFIT_CHECK_TH.md) แล้วจาก canonical Train: คน 2 + Wayu 2 ฝึกซ้ำและผ่านที่ 20 updates ไม่ใช้ Dev/Test ผลอยู่ `results/pilot/aasist_overfit_check/fixed4_20261007_v1/` ไม่แก้ dataset หรือ notebooks เดิม Accuracy 100% นี้เป็นของชุดที่ฝึกซ้ำ ไม่ใช่ผลกับเสียงใหม่

## AASIST Clean smoke 1 epoch

หลัง canonical preparation มี Dataset/window policy และ `experiments/pilot/scripts/aasist/train_aasist_clean.py` ที่ลองฝึกและตรวจ checkpoint reload แล้ว ใช้ `.venv` หลัก ไม่ใช่ notebook TTS อ่าน [คู่มือและผลครั้งแรก](aasist/AASIST_CLEAN_SMOKE_TH.md) ผลอยู่ใน `results/pilot/aasist_clean_smoke/` เป็น technical smoke เท่านั้น (Dev loss รอบแรกแย่ลง) ไม่ใช่ Final Test/การพิสูจน์ความแม่นยำ และยังไม่ใช่ RawNet2/Mixed training

## เตรียมเสียงสองคลาสเป็น mono 16 kHz

เปิด [common_voice_pilot_audio.ipynb](../notebooks/common_voice_pilot_audio.ipynb) เลือก **`.venv` หลัก** ไม่ใช่ `.venv-wayu` แล้วรันจากบนลงล่าง หรือเปิด [ผลที่รันแล้ว](../notebooks/outputs/common_voice_pilot_audio.executed.ipynb) หัวข้อ 3 มีเสียงคน/Wayu ก่อนและหลังแปลงให้ฟัง ไม่โหลด TTS ใหม่

อ่าน `wayu_pilot_train_native.csv` / `wayu_pilot_dev_native.csv` ที่ตรวจ hash กับ generation report เตรียม **200 ไฟล์ WAV FLOAT, mono, 16 kHz** ด้วย helper ร่วม `thai_spoof.cvtts.audio` มี Train คน 80 + Wayu 80 และ Dev คน 20 + Wayu 20 ไม่แก้ไฟล์ต้นทาง แปลง sample rate โดยไม่ normalize gain/clip/trim ความยาวยังเต็มคลิป ไม่ตัดเป็น 4.04 วินาทีหรือ repeat/pad ในขั้นนี้ ไม่เติม noise/telephone และยังไม่ train

ผลภายใน `data/processed/cvtts/pilot_v1/` (ไม่เข้า Git):

- เสียง: `canonical/clean16k/<split>/<label>/<sample_id>.wav`
- รายการใหม่: `manifests/wayu_pilot_train_clean16k.csv` (160) และ `wayu_pilot_dev_clean16k.csv` (40)
- รายงานเทคนิค: `qc/canonical_audio/wayu_pilot_clean16k_v1.json`

manifest เก็บ `source_audio_path`/`source_audio_file_sha256` และ source rate/channels/duration สำหรับย้อนตรวจ พร้อม output waveform/file hashes และ policy `mono16k_float_fullclip_v1` ตรวจ source hashes, readback ทั้ง 200 ไฟล์, duration error ไม่เกิน 1 target sample, duplicate/split overlap และไม่เขียนทับเมื่อข้อมูลต่าง มี tests โดยใช้เสียงที่สร้างเอง ไม่เก็บความคิดเห็นส่วนตัว

**ข้อจำกัด:** codec/sample rate ของไฟล์ปลายทางเหมือนกัน ไม่ได้ทำให้ MP3 ต้นทางไร้ artefacts หรือแบนด์วิดท์เดิมเท่ากัน ไม่ใช่ผลทดสอบคุณภาพคำอ่านทั้งชุด ขั้น canonical ไม่ train; script smoke ที่เพิ่มภายหลังเลือก window ใน memory โดยไม่แก้เสียงเต็ม ดูหัวข้อขั้นล่าสุดข้างบน

## Wayu ครบ pilot Train 80 / Dev 20

เปิด [common_voice_wayu_pilot_dataset.ipynb](../notebooks/common_voice_wayu_pilot_dataset.ipynb) เลือก **`.venv-wayu` Python 3.11** แล้วรันจากบนลงล่าง หรือดู [ผลที่รันแล้ว](../notebooks/outputs/common_voice_wayu_pilot_dataset.executed.ipynb) notebook นี้อ่าน `real_train.csv`, `real_dev.csv` และ `pilot_split_report.json` จาก EDA ไม่ต้องมี MMS หรือ manifest review10 ของ MMS

ใช้ Wayu/voice `m_young_clear`/seed 42 ต่อคลิป/speed 1.0 ตาม trial เดิม โดยสร้าง Train 80 / Dev 20 ใช้เสียงเก่าที่ตรวจ provenance ตรงกัน ไม่แทนที่ไฟล์หรือผลฟังเดิม ในเครื่องนี้มี Train 10 คลิปอยู่ก่อนแล้ว จึงเพิ่มจริง Train 70 + Dev 20 ทุกเสียงปลอมสืบทอด split ของข้อความต้นทาง ไม่มี Final Test ไม่เลือกค่าจากผล detector หรือจูนเสียงตาม Dev และยังไม่เปลี่ยนแผนวิจัยให้ใช้ TTS ตัวเดียวถาวร

เครื่องใหม่: ต้องมี Common Voice release/path เดียวกัน และรัน EDA ขั้นเตรียมทดลอง 1–3 ให้ได้ชุดเสียงคน 100 คลิปก่อน จาก project root ใช้:

```powershell
.\scripts\setup_wayu_pilot.ps1 -Dataset
```

`-Dataset` เพิ่ม [spaCy English resource 3.8.0](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0) ให้ frontend เพราะใน Train มีคำว่า `Facebook` หนึ่งข้อความ ใช้ requirements ที่ล็อกรุ่น/URL/checksum ใน [wayu-dataset-requirements.txt](../../../configs/cvtts/wayu-dataset-requirements.txt) ติดตั้งเฉพาะ `.venv-wayu` ไม่ลดรุ่นแพ็กเกจใน `.venv` หลัก

ตรวจ source hashes และ split overlap, frontend ทั้ง 100 ก่อนสร้าง, waveform finite/nonempty/nonzero, float32 WAV roundtrip และสร้างเสียงใหม่ซ้ำใน memory ตรวจความตรงกัน รายงานมี model/code/config/software/manifest hashes ไม่ใส่ความคิดเห็นส่วนตัว และ **ไม่ยืนยันว่าทั้ง 100 อ่านถูกจากการตรวจเทคนิค** อีก 90 คลิปยังไม่ได้ฟังครบ หัวข้อ 5 มีตัวอย่าง Train ใหม่ให้ฟังแบบกระจายความยาว พร้อมข้อความที่มีคำอังกฤษ ไม่ปรับ TTS ตามผลฟัง Dev

ผลใน `data/processed/cvtts/pilot_v1/` (ไม่เข้า Git):

- เสียง Wayu: `native_tts/wayu/train/` และ `native_tts/wayu/dev/`
- ที่มารายคลิป: `qc/tts_samples/<sample_id>.json`; ชุดนี้: `qc/tts_experiments/wayu_pilot_train_dev_v1.json`
- เสียงปลอม: `manifests/tts_wayu_train.csv` (80), `tts_wayu_dev.csv` (20), `tts_wayu_all.csv` (100)
- สองคลาส: `manifests/wayu_pilot_train_native.csv` (คน 80 + TTS 80), `wayu_pilot_dev_native.csv` (คน 20 + TTS 20)

**รายการ native ไม่ได้ใช้ train โดยตรง:** เสียงคนเป็น MP3 sample rate เดิม ส่วน TTS เป็น WAV 24 kHz ใช้ notebook เตรียมเสียงร่วมด้านบนเพื่อสร้างรายการ `clean16k` ก่อนใช้ AASIST smoke script ไม่มีการ resample/crop/pad/noise/telephone/fine-tune ใน notebook สร้าง Wayu ไม่อ้างว่าควบคุมทุกความต่างระหว่างคลาสแล้ว หรือว่าผล pilot เท่ากับผลวิจัย

<a id="wayu-pilot"></a>

## Wayu pilot: คลิปแรกและชุดข้อความ Train 10 คลิป

เปิด [common_voice_wayu_tts_pilot.ipynb](../notebooks/common_voice_wayu_tts_pilot.ipynb) แล้วเลือก **Select Kernel → Python Environments → .venv-wayu (Python 3.11)** รันจากบนลงล่าง หรือเปิด [ผลที่รันแล้ว](../notebooks/outputs/common_voice_wayu_tts_pilot.executed.ipynb) และฟัง 3 players ในหัวข้อ 4: เสียงคนต้นทาง → MMS เดิม → Wayu ใหม่ ข้อความเดียวกัน “ฉันไม่ได้คุยโม้” จาก Train เท่านั้น ไม่ใช่ Dev/Test

ทดลองบน CPU ด้วย voice `m_young_clear`, seed 42, speed 1.0; ผลคลิปแรกในเครื่องนี้ 1.50 วินาทีที่ native 24 kHz และ waveform ตรงกันเมื่อรันซ้ำ **ผู้ใช้ฟังยืนยันว่า “โม้ ถูก / คำครบ”** บันทึกผลเดิมไว้ใน `qc/tts_reviews/wayu_paxa_common_voice_th_25669007_m_young_clear_seed42.json` ไม่สรุปว่าอ่านถูกจาก frontend trace และไม่เพิ่มเข้า manifest train อัตโนมัติ ไม่แก้ seed probes/เสียง MMS/manifest/reviews เดิม ไม่ train detector หรือ TTS และไม่โคลนเสียงคนต้นทาง ชื่อ voice ไม่ใช่อายุ/เพศของบุคคลที่ยืนยันแล้ว

generation JSON ยังแสดง `pending` ตามสถานะขณะสร้าง ไม่แก้ provenance เดิมให้รันซ้ำยังตรวจ hash ได้; notebook อ่านผลฟังล่าสุดจาก review JSON ที่แยกไว้

**หัวข้อ 5–6: Wayu review10** ใช้ข้อความและลำดับเดียวกับ `manifests/tts_train_review10.csv` ของ MMS เลือกจาก `real_train.csv` ที่ตรวจ hash แล้วเท่านั้น ใช้ voice/seed/speed เดิม คลิป 3 ใช้เสียง Wayu เดิมที่ตรวจแล้ว อีก 9 คลิปสร้างใหม่โดยไม่แก้ข้อความ/เสียง MMS/manifest เดิม ไม่ใช้เสียงคนเป็น input ของ TTS ไม่ใช้ Dev/Test ไม่เติม noise/telephone และไม่ train ตรวจ frontend ก่อนสร้างทั้ง batch ตรวจ waveform finite/nonempty/nonzero และสร้างซ้ำใน memory ตรวจความตรงกันก่อนบันทึก มี CSV แยก `manifests/tts_wayu_train_review10.csv` พร้อม summary `qc/tts_experiments/wayu_train_review10_v1.json` และ provenance รายคลิปที่ `qc/tts_samples/` รันซ้ำจะตรวจที่มาและใช้ไฟล์เดิม ไม่เขียนทับเมื่อข้อมูลต่าง

เปิด [ผลที่รันแล้ว](../notebooks/outputs/common_voice_wayu_tts_pilot.executed.ipynb) ที่ **หัวข้อ 6** เพื่อฟัง Wayu ทีละคลิป มีข้อความและ player เสียงคนอ้างอิงด้วย ข้อความต้นทางบางข้อแปลก อย่าแก้ก่อนทดลองหรือถือว่าเสียงคนต้องอ่านถูกทุกคลิป ผลฟังคลิป 3 ไม่ใช้แทนอีก 9 ข้อ ทุกข้อยังต้องฟังตรวจคำผิด/คำหาย/วน/ขาดก่อนตัดสินขั้นถัดไป และไม่ลอกผลฟัง MMS มาใช้กับ Wayu

**ผลฟัง Wayu review10 ล่าสุด:** ผู้ใช้ยืนยันว่าอ่านถูกทั้ง 10 คลิป เก็บเฉพาะผลตรวจข้อความพร้อม manifest/audio hashes ที่ `qc/tts_reviews/` ไม่แก้ review เดิมของคลิป 3 หรือ generation provenance การผ่านด้านข้อความใน 10 ตัวอย่างนี้ยังไม่ยืนยันคุณภาพทั้งชุด หรือประสิทธิภาพ AASIST/RawNet2

น้ำหนัก [Wayu-Paxa-TTS-Edge](https://huggingface.co/wayu-ai/wayu-paxa-tts-edge) revision `8196688df56a8d08ccfa186505343adff412ab6b` ดาวน์โหลดเฉพาะ 4 ไฟล์รวมประมาณ 328 MB: config, model.pth, voice เดียว, model card โค้ด [ผู้พัฒนา](https://github.com/wayu-research/wayu-tts-inference) ที่นำมาติดตั้ง pin commit `07ab898d516649313926f0b843b809a962f993ad`; notebook และ script setup เป็นโค้ดเชื่อมกระบวนการทดลองที่เราเพิ่มเอง ไม่ใช่โมเดลที่เขียน/ฝึกเอง โมเดลหลักและ voice โหลด weights แบบ `weights_only=True` ไม่ใช้ checkpoint ที่ไม่ได้ตรวจแหล่งที่มา น้ำหนัก CC-BY-NC-4.0 / โค้ด Apache-2.0 ต้องแสดง attribution และตรวจ [เงื่อนไขการใช้](https://www.wayuresearch.org/terms) ก่อนใช้งานอื่น

แพ็กเกจ tltk 1.11 ต้องการ scikit-learn 1.2.x ซึ่งติดตั้งแบบปกติใน Python 3.12 ไม่ผ่าน จึงแยก `.venv-wayu` ใช้ Python 3.11, NumPy 1.26 และ Transformers 4.57.6 **อย่าติดตั้ง requirements นี้ลง `.venv` หลัก** รุ่นหลักของการทดลองอยู่ [wayu-pilot-requirements.txt](../../../configs/cvtts/wayu-pilot-requirements.txt); ที่มาของข้อความ โมเดล settings phonemes และ versions ที่รันจริงอยู่ใน JSON ผลแต่ละคลิป

เครื่องนี้เตรียม environment และโมเดลให้แล้ว ไม่ต้อง setup ซ้ำ หากเป็นเครื่องใหม่ที่มี `.venv` หลักแล้ว ให้รันจาก project root:

```powershell
.\scripts\setup_wayu_pilot.ps1
```

script ดาวน์โหลด Python/แพ็กเกจแยกและตรวจ dependencies แต่ **ไม่สร้างเสียงและไม่ดาวน์โหลด weights**; notebook จึงโหลด weights เมื่อยังไม่มีไฟล์ อย่าลบ `tmp/wayu-python` ระหว่างใช้ `.venv-wayu` เพราะเป็น Python ที่ environment อ้างถึง หากมี Python 3.11 ของตนเอง ใช้ `py -3.11 -m venv .venv-wayu`, ติดตั้ง PyTorch CPU แล้วติดตั้ง requirements ด้วย Python ของ environment ใหม่นั้น ไม่ต้องใช้ script bootstrap

ตำแหน่งไฟล์ (ไม่เข้า Git):

- Python/เครื่องมือ/cache สำหรับชุดนี้: `tmp/wayu-python`, `tmp/wayu-bootstrap`, `tmp/wayu-uv-cache`; environment: `.venv-wayu/`
- น้ำหนัก: `checkpoints/tts/wayu-paxa-tts-edge/<revision>/`
- เสียง: `data/processed/cvtts/pilot_v1/native_tts/wayu/train/`
- ที่มาเสียง: `data/processed/cvtts/pilot_v1/qc/tts_samples/wayu_paxa_*.json`
- notebook ที่รันแล้วและมี player: `experiments/pilot/notebooks/outputs/common_voice_wayu_tts_pilot.executed.ipynb`

source notebook ไม่มี outputs ก่อน commit; ไม่ commit dataset, น้ำหนัก หรือเสียง/รายงานผลในเครื่อง

**คลิป 3 seed probe (หัวข้อ 9–10 ใน notebook TTS):** ทดลอง seed 7/123/2026 ที่กำหนดไว้ก่อนฟัง เทียบ seed 42 โดยข้อความ “ฉันไม่ได้คุยโม้” และโมเดล/ค่าการสร้างเหมือนเดิม ตรวจ tokenizer และ roundtrip ก่อนสร้าง เก็บเสียงใหม่สามแบบพร้อมรายงานชื่อลงท้าย `_seed_probe_v1_seed...` และสรุปที่ `qc/tts_experiments/clip3_seed_probe_v1.json` ไม่แทนที่ baseline ไม่เปลี่ยน manifest review10 และยังไม่เลือก seed ที่ใช้กับชุดเต็มจนฟังตรวจ ไม่ใช้ผล detector เลือกเสียง

**MMS Thai text-preparation fix (หัวข้อ 7–8 ใน notebook TTS):** ตรวจพบว่า tokenizer ที่ pin ไว้ไม่รองรับ U+0E33 (`ำ`) และตัดออกก่อน encode จึงทดลองใช้รูป U+0E4D + U+0E32 (`ํ` + `า`) เฉพาะคลิป 10 พร้อมตรวจข้อความหลัง tokenizer และ token roundtrip ใช้ helper `thai_spoof.cvtts.text` ที่มี tests บันทึกข้อความเดิม/ข้อความเข้า TTS/normalization version และเสียงใหม่ชื่อ `_sara_am_v1_seed42` แยกจาก baseline 10 คลิป ไม่แก้ manifest เดิม ไม่เปลี่ยนคลิป 3 และยังรอฟังตรวจ หัวข้อ 1–6 คงไว้เพื่อเทียบ baseline ที่มีข้อผิดพลาด ห้ามนำไปสร้างชุดเต็มโดยไม่ใช้ policy ที่ตรวจแล้ว

**ขั้นที่ 4 (แยกจาก EDA):** เปิด [common_voice_tts_pilot.ipynb](../notebooks/common_voice_tts_pilot.ipynb) เพื่ออ่านข้อความจาก Train และใช้ MMS Thai ที่ล็อก revision สร้างเสียงสังเคราะห์เพียง 1 คลิป รันใน `.venv` บน CPU; optional dependencies อยู่ใน `.[tts]` โมเดลดาวน์โหลดครั้งแรกประมาณ 145 MB และอยู่ `checkpoints/tts/` ไม่โหลด remote code/weights pickle ไม่ส่งเสียงคนให้ API และไม่ทำ voice cloning ไฟล์เสียงอยู่ `data/processed/cvtts/pilot_v1/native_tts/mms_tha/train/` พร้อม JSON ที่ `qc/tts_samples/` ต้องฟังตรวจเองก่อนสร้างเพิ่ม (status `pending`) ไม่ถือว่าชุดสองคลาสพร้อม train แล้ว ผลที่รันแล้วเก็บใน [outputs/common_voice_tts_pilot.executed.ipynb](../notebooks/outputs/common_voice_tts_pilot.executed.ipynb) โมเดลมีข้อจำกัด CC-BY-NC 4.0 ตาม [model card](https://huggingface.co/facebook/mms-tts-tha)

เปิด [common_voice_eda.ipynb](../notebooks/common_voice_eda.ipynb) ใน VS Code เลือก **Select Kernel → Python Environments → .venv** แล้วกด **Run All** หรือรันทีละเซลล์จากบนลงล่าง เริ่มด้วย `pd.read_csv()`, `df.head()`, `df.shape`, `df.info()` และ `df.columns`

**TTS review batch:** หัวข้อ 5–6 ของ `common_voice_tts_pilot.ipynb` เพิ่มตัวอย่าง Train ให้ครบ 10 คลิป รวมคลิปแรกและอีก 9 ข้อความที่กระจายตามความยาวข้อความ ใช้โมเดล/การตั้งค่า/seed เดิม ตรวจ hash ก่อนใช้ไฟล์ที่มีแล้ว ไม่ใช้ Dev และไม่สร้างครบ 100 คลิป รายการอยู่ `data/processed/cvtts/pilot_v1/manifests/tts_train_review10.csv` ผลฟังจริงจากผู้ใช้เก็บแยกใน `qc/tts_reviews/` เพื่อไม่แก้ provenance เดิม; อีก 9 คลิปยังรอฟังตรวจ มี player ทีละข้อท้าย notebook

สิ่งที่ดูได้: ไฟล์ TSV ทั้งแพ็กและบทบาท, จำนวนคลิป, 13 คอลัมน์ต้นทาง, ค่าว่าง, ชื่อไฟล์/ข้อความซ้ำ, ความยาวเสียงและคลิปที่เกิน 4.04/6/8 วินาที, อายุ/เพศ/สำเนียง, speaker keys, โหวต, ข้อความ, ไฟล์เสียงที่มีจริง และ sample rate/channels ของตัวอย่าง 5 คลิป พร้อมฟังตัวอย่างหนึ่งคลิป

ใช้ pandas ตรงใน notebook ไม่ต้องเรียก helper หรือ CLI ใหม่ ข้อมูลดิบที่ใช้คือ `data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/` ส่วนผลที่รันแล้วอยู่ [outputs/common_voice_eda.executed.ipynb](../notebooks/outputs/common_voice_eda.executed.ipynb) ในเครื่องนี้และไม่เข้า Git

`df` คือ validated; `df_all` รวม validated/invalidated/other เท่านั้น Train/Dev/Test ต้นทางเป็นส่วนย่อยจึงไม่บวกซ้ำ คอลัมน์ `clip_status`/`duration_s` เป็นสิ่งที่เติมเองเพื่อดูข้อมูล ไม่ใช่ฟีเจอร์ต้นทางหรือ input โมเดล

ความยาวในส่วน EDA อ่านจาก metadata ไม่ใช่ decode ทุกไฟล์; ขั้นเตรียมทดลอง 2 อ่านเสียงเต็มเฉพาะชุด 100 คลิป จำนวน client_id คือรหัสผู้พูดไม่ซ้ำในต้นทาง ยังไม่ยืนยันจำนวนบุคคลจริง Notebook ไม่แก้ raw data ไม่สร้าง TTS และไม่ train

ท้าย notebook มี **ขั้นเตรียมทดลอง 1**: สร้าง `df_candidates` จาก validated โดยเก็บเฉพาะแถวที่ `client_id`, `path`, `sentence` ไม่ว่าง พร้อมนับจำนวนก่อน/หลังคัด

**ขั้นเตรียมทดลอง 2**: สร้าง `df_pilot` ชุดเล็ก 100 คลิปด้วย seed 42 เลือกหนึ่งคลิปต่อรหัสผู้พูดและไม่ซ้ำข้อความหลัง Unicode/whitespace normalization อ่านเสียงเต็มคลิป ตรวจเสียงว่าง/NaN/infinity/เงียบเกือบศูนย์ และ hash เสียงที่ decode แล้วว่าซ้ำกันภายในชุดนี้หรือไม่ หากมีปัญหาจะหยุด ไม่ลบหรือข้ามไฟล์อัตโนมัติ มีเซลล์ฟังตัวอย่างจากชุดนี้ด้วย นี่เป็น pilot เพื่อเช็กกระบวนการ ไม่ใช่ Final Test หรือชุดสำหรับสรุปผลวิจัย ยังไม่แบ่ง Train/Dev ไม่แปลงเสียงและไม่สร้าง TTS การตรวจเสียงซ้ำครอบคลุมเฉพาะ 100 คลิป ไม่ใช่ทั้ง corpus

ก่อน commit notebook ต้นแบบให้ clear outputs; เก็บไฟล์ที่มีผลจริงใน `outputs/` แผนงานฉบับละเอียดอยู่ใน [workflow Phase 1](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s08)

**ขั้นเตรียมทดลอง 3**: แบ่งชุด pilot เป็น Train 80 / Dev 20 ด้วย seed 43 และตรวจรหัสผู้พูด ข้อความที่ normalize ชื่อไฟล์ decoded PCM hash และ file hash ว่าไม่มีรายการร่วมกันข้ามชุด บันทึก `real_all.csv`, `real_train.csv`, `real_dev.csv` ใน `data/processed/cvtts/pilot_v1/manifests/` และ `pilot_split_report.json` ใน `qc/` พร้อม seeds, source metadata hash และ manifest hashes รันซ้ำได้เมื่อข้อมูลตรงเดิม แต่จะหยุดถ้าผลต่างจากไฟล์ version เดิม

รายการที่บันทึกยังเป็น MP3 native sample rate และมีเฉพาะ label `bonafide` ไม่ใช่ข้อมูลที่พร้อม train สองคลาสหรือ manifest สำหรับสั่ง CLI เดิมทันที `audio_path` เป็น path จาก project root; `path` คือชื่อไฟล์ต้นทาง ไม่คัดลอกเสียง 100 ไฟล์ เมื่อสร้าง TTS ต้องให้เสียงปลอมสืบทอด split จากข้อความต้นทาง ชุดนี้ไม่มี Final Test และไม่ใช้รายงานประสิทธิภาพสุดท้าย รหัสผู้พูด/ข้อความ/เสียงของ pilot ต้องกันออกจาก Final Test ที่จัดภายหลังด้วย
