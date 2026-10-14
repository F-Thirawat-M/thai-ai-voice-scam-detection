# Research protocol v2 (สรุปที่ใช้ยึด)

ตกลงเมื่อ: 14 ตุลาคม 2026 โดยผู้ใช้ · สถานะ: ใช้เป็นแนวทางหลัก; อาจารย์ยังไม่ได้ยืนยันทุกข้อ

เอกสารนี้สรุปคำถามวิจัย สมมติฐาน ตัวแปร และวิธีทดลองฉบับล่าสุด **เมื่อขัดกับ `COMMON_VOICE_PROJECT_WORKFLOW_TH.md` ให้ยึดเอกสารนี้** ส่วนรายละเอียดทางเทคนิคที่เอกสารนี้ไม่ได้พูดถึง (split, leakage, data contracts, gates) ยังใช้ตาม workflow

## 1. หัวข้อและขอบเขต

การจำแนกเสียงมนุษย์และเสียงสังเคราะห์ AI ภาษาไทยสำหรับป้องกันมิจฉาชีพทางโทรศัพท์

- เสียงจริง: Common Voice Thai 27.0
- เสียงปลอม: **zero-shot voice cloning** ของผู้พูด Common Voice จากคลิปอื่นของคนเดียวกัน
- ช่องสัญญาณ: เติมเสียงรบกวนจำลอง และช่องสัญญาณโทรศัพท์จำลอง (narrowband + G.711)
- นอกขอบเขต: โทรศัพท์จริง/VoIP, ตัดสินเจตนาฉ้อโกง, ระบุตัวบุคคล, ฝึก generator ใหม่

## 2. ชื่อเรียก (ใช้แทน Clean/Mixed ทั้งเล่ม สไลด์ config)

| เดิม | ใหม่ (ไทย) | ใหม่ (อังกฤษ) / config id |
| --- | --- | --- |
| Clean (สภาพเสียง) | เสียงต้นฉบับ | Original / `original` |
| Noise X dB | เติมเสียงรบกวน X dB | Added noise / `noise_10db`, `noise_5db` |
| Telephone | จำลองสายโทรศัพท์ | Simulated telephone / `telephone_v1` |
| Clean arm | ฝึกด้วยเสียงต้นฉบับอย่างเดียว | Original-only training / `orig` |
| Mixed arm | ฝึกด้วยเสียงหลายสภาพ | Multi-condition training (MCT) / `mct` |

## 3. คำถามวิจัยและสมมติฐาน

| | สมมติฐาน | เทียบ | เกณฑ์ตัดสิน (ล็อกก่อนเปิด Test) |
| --- | --- | --- | --- |
| H0 | fine-tune ด้วยข้อมูลไทยทำให้ EER ต่ำกว่า pretrained เดิม | fine-tuned (`orig`) vs pretrained บน Test เสียงต้นฉบับ | ΔEER < 0 และ bootstrap 95% CI ไม่คร่อม 0 |
| H1 | โมเดลที่ฝึกด้วยเสียงต้นฉบับอย่างเดียว EER สูงขึ้นในสภาพเติมเสียงรบกวน/จำลองโทรศัพท์ | `orig` บน noise/telephone vs `orig` บน original | ΔEER > 0 และ CI ไม่คร่อม 0 แยกแต่ละสภาพ |
| **H2 (หลัก)** | ฝึกด้วยเสียงหลายสภาพลด EER บน noise/telephone | `mct` vs `orig` โมเดลเดียวกัน สภาพเดียวกัน | ΔEER = EER_mct − EER_orig < 0, paired cluster bootstrap CI ไม่คร่อม 0, ทิศเดียวกันทั้ง 3 seeds |
| H3 | ฝึกหลายสภาพไม่ทำให้ EER บนเสียงต้นฉบับแย่ลงเกิน 2 percentage points | `mct` vs `orig` บน original | ขอบบนของ CI ของ ΔEER ≤ +2.0 pp |
| H4 | เสียง cloning ตรวจยากกว่าเสียง TTS เสียงสำเร็จรูป | EER บน Test แยกตาม generator (เฉพาะเมื่อมี Wayu เป็นชุดทดสอบ) | EER_clone > EER_wayu, CI ไม่คร่อม 0 (วิเคราะห์เสริม) |

- ทุกสมมติฐานทดสอบแยก AASIST และ RawNet2; สรุปว่า "ผลเกิดซ้ำ" เมื่อผลไปทางเดียวกันทั้งสองโมเดล ไม่เทียบว่าโมเดลไหนชนะ
- ผลไม่ตรงสมมติฐานรายงานตามจริง ไม่เปลี่ยนเกณฑ์หลังเห็นผล
- เหตุผลของ margin 2 pp: เล็กพอที่ผู้ใช้งานจริงแทบไม่รู้สึก แต่ใหญ่กว่าความละเอียดของ EER บน Test หลายร้อยคลิปต่อคลาส

## 4. ตัวแปร

| บทบาท | ตัวแปร | ค่า |
| --- | --- | --- |
| **ตัวแปรต้น** | สภาพข้อมูลที่ใช้ fine-tune | `orig` vs `mct` (original / noise / telephone อย่างละ 1/3) |
| ทำซ้ำบน | ตัวตรวจจับ | AASIST, RawNet2 (pretrained ของแต่ละตัว) |
| **ตัวแปรตาม** | EER บน Test แยกสภาพเสียง | original, noise_10db, noise_5db, telephone_v1; รองลงมา FAR/FRR ที่ threshold จาก Dev |
| ควบคุม: generator | model + revision, ค่า default ที่ต้นทางแนะนำ, seed ตายตัวต่อคลิป, `tts_text` = ข้อความของคลิปจริงที่จับคู่, คลิปต้นแบบ 2–8 วินาทีของผู้พูดเดียวกัน | สร้างครั้งเดียว freeze ใช้ไฟล์ชุดเดียวกันทุกสูตร |
| ควบคุม: เสียง | mono 16 kHz, `resample_poly`, ไม่ normalize, window 64,600 samples, Train random crop / Dev-Test ช่วงแรก / คลิปสั้น repeat | เหมือน pilot |
| ควบคุม: noise | SNR **10 และ 5 dB** (ตาม Ass6) ทั้ง Train และ Test; noise pool แยก recording ตาม split | Train สุ่ม 10/5 เท่ากัน |
| ควบคุม: telephone | band-pass 300–3,400 Hz Butterworth N=6 → 8 kHz → G.711 μ-law → 16 kHz | workflow ข้อ 12.4 |
| ควบคุม: การฝึก | pretrained hash เดียวกัน, AdamW lr 1e-5, wd 1e-4, microbatch 2 × accum 8, updates เท่ากัน, label 1:1, spoof สุ่ม generator เท่ากัน, seeds **42/43/44** | AASIST ใช้ Frozen BN เป็นค่าเริ่ม แต่ต้องยืนยันบนข้อมูล cloning ใน pilot ก่อนล็อก |
| ควบคุม: ประเมิน | Test ชุดเดียวกันทุกสูตร, threshold จาก Dev, EER แบบ linear interpolation | workflow ข้อ 13 |

## 5. Generators

| บทบาท | Model | หมายเหตุ |
| --- | --- | --- |
| G1 (ฝึก + ทดสอบ) | `VIZINTZOR/F5-TTS-THAI` | ฝึกจาก Common Voice Thai → บันทึกเป็นข้อจำกัด pretraining overlap |
| G2 (ฝึก + ทดสอบ) | `k2-fsa/OmniVoice` | ถ้าไม่ผ่าน pilot ใช้ Wayu 12 voices (กระจายสมดุลด้วย hash ของ text id) แทน และตัด H4 |
| ชุดทดสอบเสริม | Wayu 12 voices | ไม่ใช้ฝึก/เลือก checkpoint; ใช้ตอบ H4 และ RQ3 (generator ที่ไม่เคยเห็น) |

## 6. วิธีทดลอง (ลำดับ)

1. คัด cohort จาก `validated.tsv`: ผู้พูดต้องมี ≥ 2 คลิป (คลิปหนึ่งเป็นเสียงจริงที่จับคู่ อีกคลิปเป็นต้นแบบสำหรับ clone)
2. แบ่ง Train/Dev/Test ตามผู้พูด + ข้อความ + duplicate ก่อนสร้างเสียง (workflow ข้อ 9) กันผู้พูด/ข้อความของ pilot_v1 ออกจาก Test
3. สร้างเสียง clone ด้วย G1/G2: ข้อความเดียวกับคลิปจริงที่จับคู่, ต้นแบบเป็นคนละคลิป, freeze base manifest
4. ตรวจ shortcut: เทียบ noise floor, bandwidth, RMS, ความยาวเงียบ ระหว่างจริงกับปลอม และลอง classifier ง่าย ๆ บนสถิติเหล่านี้ ถ้าแยกได้เกือบสมบูรณ์ต้องแก้ก่อนไปต่อ
5. สร้างสภาพเสียง original / noise 10, 5 dB / telephone ให้ทั้งจริงและปลอมเหมือนกัน
6. Fine-tune 2 โมเดล × 2 สูตร × 3 seeds = 12 runs
7. เลือก checkpoint จาก Dev ด้วย `(EER_original + mean(EER_noise10, EER_noise5) + EER_telephone) / 3`; เลือก threshold จาก Dev รวมสามสภาพ แล้วล็อก
8. เปิด Test ครั้งเดียว รายงาน EER ทุก run/seed/สภาพ/generator แล้วตัดสิน H0–H4 ตามเกณฑ์ข้อ 3

## 7. จริยธรรมและข้อมูล

- การ clone ผู้พูด Common Voice เป็นการตัดสินใจของผู้ใช้ (14 ต.ค. 2026) เพื่อการวิจัยตรวจจับเท่านั้น; ควรแจ้งอาจารย์และบันทึกคำตอบใน decision log
- ห้ามเผยแพร่/commit เสียงที่ clone, เสียงต้นแบบ, ID ผู้พูด หรือ metadata รายคลิป; ห้ามพยายามระบุตัวตนผู้พูด
- รายงานในเล่มเป็นสถิติรวมเท่านั้น
