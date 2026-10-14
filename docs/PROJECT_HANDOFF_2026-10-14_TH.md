# ส่งต่อโครงงานตรวจจับเสียงสังเคราะห์ภาษาไทย

อัปเดต: 14 ตุลาคม 2026 (Asia/Bangkok)

สถานะ: ทำ feasibility pilot ของ AASIST แล้ว; การทดลองวิจัยหลักยังไม่เริ่ม ข้อมูลนี้ตรวจจากโค้ดและรายงานผลในเครื่องประกอบกับเค้าโครงฉบับร่างและข้อกำหนดจากผู้ใช้

- Project root: `D:/KKU_files/year3_semester1/CP353761/project`
- Repository: `https://github.com/F-Thirawat-M/thai-ai-voice-scam-detection`
- Local branch/HEAD ที่ตรวจ: `main`, `50e2cee` (merge PR #16 รวมงาน BatchNorm/Frozen BN/seed check) การตรวจครั้งนี้ไม่ได้ fetch สถานะ remote ใหม่
- ผู้ใช้รับผิดชอบ AASIST; เพื่อนรับผิดชอบ RawNet2 สถานะ RawNet2 ในเอกสารนี้หมายถึงสิ่งที่มีใน repository นี้ ไม่ยืนยันงานที่อาจอยู่ในเครื่องเพื่อน
- หลักฐานผลจริงอยู่ใน JSON/CSV/checkpoints ใต้ `results/pilot`; เอกสารแผนไม่ใช่หลักฐานว่ารันสำเร็จ
- แหล่งแผนล่าสุดที่ผู้ใช้ให้ตรวจ: [เค้าโครง Ass6](D:/KKU_files/year3_semester1/CP353761/Ass6/Ass6_เอกสารเค้าโครงฉบับร่าง.pdf) โดยเฉพาะข้อ 5-6 หน้า PDF 8-10 สถานะยังเป็นฉบับร่าง ไม่พบหลักฐานว่าอาจารย์อนุมัติค่าทางเทคนิคทุกข้อแล้ว
- เอกสาร workflow เก่าใน repo มีค่าบางส่วนต่างจาก Ass6 โดยเฉพาะ Noise SNR และเกณฑ์เลือก checkpoint ต้องจัดให้ตรงกันก่อน main experiment

## 1. เป้าหมายและขอบเขตของโปรเจกต์

ชื่อโครงงาน: การจำแนกเสียงมนุษย์และเสียงสังเคราะห์ AI ภาษาไทยสำหรับป้องกันมิจฉาชีพทางโทรศัพท์

คำถามวิจัยหลัก: การ fine-tune ตัวตรวจจับด้วยข้อมูลผสม Clean, Noise และ Telephone ช่วยลดความผิดพลาดบนเสียงรบกวนและเสียงจำลองโทรศัพท์ เมื่อเทียบกับการฝึกด้วย Clean เพียงอย่างเดียวหรือไม่ โดยศึกษาทั้ง AASIST และ RawNet2

| สูตรหลักที่วางแผน | ตัวตรวจจับ | ข้อมูล fine-tune |
| --- | --- | --- |
| A | AASIST | Clean |
| B | AASIST | Mixed: Clean + Noise + Telephone |
| C | RawNet2 | Clean |
| D | RawNet2 | Mixed: Clean + Noise + Telephone |

ขอบเขตที่ตกลงใช้เป็นแนวทางปัจจุบัน:

- จำแนกสองกลุ่ม: `bonafide` (เสียงจริง) และ `spoof` (เสียงสังเคราะห์จาก TTS)
- ใช้เสียงอ่านและข้อความภาษาไทยจาก Common Voice; ใช้ pretrained TTS สร้างเสียงสังเคราะห์ทั้งคลิป
- Fine-tune ตัวตรวจจับจาก pretrained checkpoint ของแต่ละสถาปัตยกรรม
- พัฒนาต้นแบบรับไฟล์เสียง แสดงกลุ่มที่ทำนาย คะแนน และข้อจำกัด
- Clean หมายถึงยังไม่เพิ่มความผิดเพี้ยนของโครงงาน อาจมี noise เดิมจากการบันทึก
- Mixed หมายถึงฝึกด้วยตัวอย่างจากสามสภาพ ไม่ได้หมายถึงใส่ noise และ telephone ต่อกันทุกคลิป
- ใช้ Dev พัฒนา/เลือกวิธีภายใต้งบที่กำหนด แล้วล็อกวิธีก่อน Final Test

นอกขอบเขตหลัก: ฝึก TTS ใหม่, voice cloning บุคคล, ยืนยันตัวผู้พูด, ระบุว่าเสียงมาจาก TTS ใด, ตรวจเสียงปลอมทุกประเภท, เชื่อมต่อสายโทรศัพท์สด และตัดสินว่าผู้โทรเป็นมิจฉาชีพ การตรวจพบเสียงสังเคราะห์ไม่ใช่หลักฐานยืนยันการฉ้อโกง

การทดลองสี่สูตรตอบผลของ training condition; ยังไม่พิสูจน์ว่าหลาย TTS ดีกว่า TTS เดียว หรือการปรับ pitch ลด overfitting หากจะอ้างประเด็นเหล่านี้ต้องมี ablation เพิ่ม

## 2. Dataset ที่ใช้: แหล่งที่มา ขนาด และการเตรียมข้อมูล

### 2.1 Common Voice ภาษาไทย

ใช้ Common Voice Scripted Speech 27.0 ภาษาไทย จาก Mozilla Data Collective รุ่นในเครื่อง `cv-corpus-27.0-2026-09-11` ข้อมูลอยู่ที่ [โฟลเดอร์ภาษาไทย](D:/KKU_files/year3_semester1/CP353761/project/data/raw/common_voice/cv-corpus-27.0-2026-09-11/th)

นับจากไฟล์ในเครื่องวันที่จัดทำเอกสาร:

| รายการ | จำนวน |
| --- | ---: |
| MP3 ภายใน `clips` ทั้งโฟลเดอร์ | 366,656 ไฟล์ |
| แถวใน `validated.tsv` | 148,823 แถว |
| `client_id` ไม่ว่างและไม่ซ้ำใน validated | 6,518 รหัส |
| คอลัมน์ใน validated | 13 |

13 คอลัมน์คือ `client_id`, `path`, `sentence_id`, `sentence`, `sentence_domain`, `up_votes`, `down_votes`, `age`, `gender`, `accents`, `variant`, `locale`, `segment`

จำนวน MP3 ทั้งโฟลเดอร์ไม่ใช่จำนวนตัวอย่างที่ใช้ฝึก และ `client_id` เป็นรหัสผู้ร่วมบันทึก ไม่ใช่จำนวนบุคคลที่ผ่านการยืนยันตัวตน การมีคอลัมน์ demographic ไม่ได้แปลว่าข้อมูลครบทุกคลิป

ข้อมูลอายุ/เพศ/สำเนียงเป็น metadata ประกอบ ไม่ได้ป้อนให้ detector ใน pilot ปัจจุบัน และไม่ควรนำ demographic ของเสียงจริงไปถือเป็น demographic ของเสียง TTS ที่สร้างจากข้อความเดียวกัน

### 2.2 Pilot ที่ใช้ฝึกจริง

เลือกจาก validated โดยมีไฟล์เสียง ข้อความ และรหัสผู้พูดพร้อมใช้ สุ่มด้วย seed 42 แล้วเลือกหนึ่งคลิปต่อ `client_id` และข้อความไม่ซ้ำ จนครบ 100 คลิป

- Text key: Unicode NFC, รวม whitespace และ `casefold()` ใช้ตรวจซ้ำโดยไม่แก้ `sentence` ต้นฉบับ
- ตรวจเสียงและ hash ก่อนแบ่งข้อมูล
- แบ่งด้วย split seed 43 เป็นเสียงจริง Train 80 / Dev 20
- ตรวจไม่ให้ `client_id`, normalized text, path, PCM hash และ file hash ซ้ำข้าม split
- สร้าง Wayu จากข้อความของแต่ละ split ให้เสียงจริงและเสียงสังเคราะห์คู่กันสืบทอด split เดียวกัน

| Split | เสียงจริง | Wayu spoof | รวม |
| --- | ---: | ---: | ---: |
| Train | 80 | 80 | 160 |
| Dev | 20 | 20 | 40 |
| รวม | 100 | 100 | 200 |

Pilot ยังไม่มี Test และไม่มี TTS ตัวที่สองใน corpus ที่ใช้ฝึก detector ผลจาก MMS เป็นการทดลองสร้างเสียงก่อนหน้า ไม่ได้รวมใน 200 คลิปนี้

ตำแหน่งชุดข้อมูล: [pilot_v1](D:/KKU_files/year3_semester1/CP353761/project/data/processed/cvtts/pilot_v1)

### 2.3 TTS และ provenance

| รายการ | Wayu ที่ใช้ใน pilot | MMS ที่ทดลองก่อนหน้า |
| --- | --- | --- |
| Model ID | `wayu-ai/wayu-paxa-tts-edge` | `facebook/mms-tts-tha` |
| Model revision | `8196688df56a8d08ccfa186505343adff412ab6b` | `fcecc37a91566f4a36ba6c6c8aa39830ff6daa9d` |
| สถานะ | สร้าง 100 คลิปสำหรับ Train/Dev | พบคำอ่านผิด จึงยังไม่ใช้ใน corpus detector |
| การสร้างเสียง | CPU, seed 42 ต่อคลิป, speed 1.0, voice `m_young_clear` | CPU, ทดลอง seed และการเตรียมข้อความ |
| Native sample rate | 24 kHz | 16 kHz |

Wayu inference code pin ที่ commit `07ab898d516649313926f0b843b809a962f993ad` ใช้ `wayu-tts==0.1.0`, `kokoro==0.9.4`, `transformers==4.57.6` ใน environment แยก

Wayu API รุ่นที่ติดตั้งรับ `text`, `voice`, `speed`, `seed`; ไม่มี `pitch` โดยตรง ในเครื่องมี voice pack `m_young_clear` เพียงตัวเดียว การเปลี่ยน seed ไม่ได้เท่ากับเปลี่ยนผู้พูดหรือ pitch

Model card ของ Wayu revision ที่เก็บในเครื่องระบุ `cc-by-nc-4.0`; ก่อนเลือก TTS เพิ่มหรือเผยแพร่ dataset ให้ตรวจและบันทึกเงื่อนไขของรุ่นนั้น การใช้โค้ด inference กับการใช้ model weights ต้องแยกตรวจ ไม่ถือว่าสิทธิ์ของทั้งสองเหมือนกันโดยอัตโนมัติ

เก็บ model/code revision, seed, voice, speed, ข้อความต้นทาง, split, hash ของ model/เสียง/manifest และรายงาน QC ไว้แล้ว มีการตรวจสร้างซ้ำสำหรับเสียงใหม่ และตรวจ provenance ของเสียงเดิมที่นำกลับมาใช้ การตรวจทางเทคนิคไม่รับรองว่าทุกคำของทั้ง 100 คลิปถูกต้องจากการฟังมนุษย์

### 2.4 การเตรียมเสียงร่วม

Canonical policy: `mono16k_float_fullclip_v1`

- Decode ด้วย SoundFile; mean-downmix ช่องเสียง; resample ด้วย `scipy.signal.resample_poly`
- บันทึก WAV subtype `FLOAT`, mono, 16 kHz และเก็บเต็มความยาวคลิป
- ไม่ normalize peak, hard-clip, trim silence, เติม noise/telephone หรือตัดหน้าต่างในขั้น canonical
- ตรวจ finite/nonempty/nonzero, source hashes, float32 WAV roundtrip, ความคลาดเคลื่อนระยะเวลาไม่เกินหนึ่ง sample และข้อมูลซ้ำข้าม split
- รายงาน canonical พบ duplicate file/waveform hashes และ cross-split source/output overlap เป็น 0 ตามรายการที่ตรวจ
- การแปลงเป็น WAV/16 kHz ไม่ได้ลบร่องรอย codec หรือความกว้างย่านเสียงของไฟล์ต้นทางทั้งหมด

| Canonical split | ความยาวต่ำสุด-สูงสุด | ระยะเวลารวมโดยประมาณ |
| --- | --- | ---: |
| Train 160 คลิป | 1.125-9.096 วินาที | 0.145524 ชั่วโมง |
| Dev 40 คลิป | 1.325-6.768 วินาที | 0.037194 ชั่วโมง |
| รวม 200 คลิป | เก็บเต็มคลิป | 0.182718 ชั่วโมง หรือ 10.96 นาที |

Manifest ฝึกจริง: [Train](D:/KKU_files/year3_semester1/CP353761/project/data/processed/cvtts/pilot_v1/manifests/wayu_pilot_train_clean16k.csv) และ [Dev](D:/KKU_files/year3_semester1/CP353761/project/data/processed/cvtts/pilot_v1/manifests/wayu_pilot_dev_clean16k.csv)

### 2.5 Window ที่เข้า detector

ใช้ 64,600 samples ที่ 16,000 Hz = 4.0375 วินาทีต่อ input

- Train: สุ่มจุดเริ่มแบบ inclusive หนึ่งครั้งต่อคลิปตาม training seed และใช้หน้าต่างเดิมตลอดสาม epochs
- Dev: ใช้ช่วงแรก
- คลิปสั้น: ต่อ waveform เดิมซ้ำด้วย `np.tile` แล้วตัดให้ครบ
- คลิปยาว: เลือกหนึ่งช่วง จึงไม่ได้ใช้เสียงครบทุกวินาทีใน pilot ปัจจุบัน
- ไม่เปลี่ยนไฟล์ canonical ต้นฉบับ และไม่มีการ normalize/noise เพิ่มใน window helper

โค้ดหลัก: [windows.py](D:/KKU_files/year3_semester1/CP353761/project/src/thai_spoof/cvtts/windows.py) และ [strict dataset loader](D:/KKU_files/year3_semester1/CP353761/project/src/thai_spoof/pilot/pilot_data.py)

4.04 วินาทีเป็น window policy ของ baseline ไม่ใช่ความยาวไฟล์สูงสุด การเปลี่ยน window/padding ต้องตรวจ config, loader, assertions และการบันทึกผลร่วมกัน ก่อนเปรียบเทียบด้วย Dev

### 2.6 Dataset ที่เลิกใช้ในแผนปัจจุบัน

SEA-Spoof และ Typhoon Thai Dialect Isan เคยอยู่ในแผนเดิม แต่ผู้ใช้เปลี่ยนมาใช้ Common Voice + TTS และอนุญาต cleanup เมื่อ 3 ตุลาคม 2026 แล้ว อย่านำ pipeline หรือจำนวนข้อมูลเก่ามาปะปนกับงานหลักปัจจุบัน การวิเคราะห์ความผิดพลาดรายอายุ/เพศ/ถิ่นยังไม่ใช่ผลทดลองที่ทำแล้วใน pilot นี้

## 3. วิธีการ/โมเดลที่เลือก และเหตุผลที่เลือก

### 3.1 ตัวตรวจจับและความรับผิดชอบ

**AASIST:** ใช้ official implementation ใต้ [external/aasist](D:/KKU_files/year3_semester1/CP353761/project/external/aasist) รับ raw waveform และใช้ spectral/temporal graph attention เป็นตัวตรวจจับหลักฝั่งผู้ใช้ มี pretrained checkpoint สำหรับเริ่ม fine-tune และสามารถตรวจเส้นทางฝึก/โหลดน้ำหนักซ้ำได้ เหตุผลเลือกคือเป็น baseline anti-spoofing ที่เปรียบเทียบกับ RawNet2 ได้ ไม่ใช่มีหลักฐานแล้วว่าดีกว่าบนภาษาไทย

**RawNet2:** ใช้ anti-spoofing implementation จาก repository ของเพื่อน `Nattadol/thai-audio-deepfake` commit `a0772432245d30601ee9e171006016fbc575f2d1` อ้างที่มาเดิมของ Tak และเก็บ MIT license ใช้ sinc-based frontend, residual blocks และ GRU จึงเป็นสถาปัตยกรรมเปรียบเทียบที่ต่างจาก graph attention ของ AASIST มี inference adapter/ตัวเตรียม checkpoint แล้ว; trainer ใน repo นี้ยังไม่มี

น้ำหนักเริ่มต้นอยู่ที่ [AASIST.pth](D:/KKU_files/year3_semester1/CP353761/project/checkpoints/aasist/AASIST.pth) และ [RawNet2 pretrained](D:/KKU_files/year3_semester1/CP353761/project/checkpoints/rawnet2/pre_trained_DF_RawNet2.pth) แยกจาก checkpoint หลังฝึก

**Wayu:** เลือกสำหรับ pilot เพราะตัวอย่างภาษาไทยที่ผู้ใช้ฟังตรวจอ่านครบกว่า MMS ในคำที่มีปัญหา และสร้างเสียงในเครื่องพร้อมบันทึก provenance ได้ หลักฐานเป็น sample QC ไม่ใช่ผล benchmark ว่า Wayu ดีที่สุด

**FastSpeech 2:** อยู่ในเค้าโครงเป็นทฤษฎีเกี่ยวกับ pitch/energy/duration ไม่ได้ยืนยันว่าจะใช้เป็น generator จริง และไม่มีผลทดลอง FastSpeech 2 ในโครงการนี้

### 3.2 Recipe ของ AASIST Frozen BN pilot ที่รันแล้ว

| ค่า | การตั้งค่า |
| --- | --- |
| เริ่มต้น | โหลด pretrained AASIST ใหม่ทุก run ไม่ต่อจาก smoke/overfit checkpoint |
| Parameters | 297,866; trainable ทั้งหมด |
| Optimizer | AdamW, learning rate `1e-5`, weight decay `1e-4` |
| Microbatch / accumulation | 2 / 8; effective batch 16 เมื่อครบกลุ่ม |
| งบฝึก | 3 epochs, 10 optimizer updates ต่อ epoch, รวม 30 updates |
| จำนวนตัวอย่าง | Train เดิม 160 คลิป; 480 clip exposures ตลอดสาม epochs |
| Loss | Unweighted Cross-Entropy; `spoof=0`, `bonafide=1` |
| Precision / clipping | float32, ไม่มี AMP, gradient norm clip 1.0 |
| BatchNorm | Frozen running statistics; affine scale/bias ยัง trainable |
| Dropout | เปิดระหว่างฝึก; ปิดขณะวัด Train/Dev |
| อื่น ๆ | num_workers 0, LR คงที่, ไม่มี frequency masking/Noise/Telephone |
| Seeds | 42, 43, 44 เปลี่ยน crop/shuffle/dropout; split เดิม |
| Selection ของ pilot | Dev CE ต่ำสุดใน epochs 1-3; ถ้าเสมอกันเลือก epoch แรก |
| Resume / early stopping | ยังไม่มี; script จำกัดงบสาม epochs |

BatchNorm มีอยู่ใน AASIST ต้นฉบับแล้ว เช่น [AASIST.py:482](D:/KKU_files/year3_semester1/CP353761/project/external/aasist/models/AASIST.py:482) โค้ดของโครงการเพิ่มการเลือกโหมดที่ [batchnorm.py](D:/KKU_files/year3_semester1/CP353761/project/src/thai_spoof/pilot/batchnorm.py)

Frozen BN ใช้สถิติ pretrained ปรับสเกล activations ระหว่าง Train ด้วย และหยุดอัปเดต running buffers ขณะที่ BN affine parameters และน้ำหนักโมเดลยังเรียนรู้ Dropout ยังเปิด จึงต่างจากการสั่ง eval ทั้งโมเดลในการทดสอบจำ 4 คลิป

Gradient accumulation ไม่ทำให้ BN เห็น batch 16 พร้อมกัน; BN ปกติยังคำนวณจาก activations ใน microbatch ละ 2 คลิป ผล Frozen BN ที่ดีขึ้นยังไม่พิสูจน์ว่า batch เล็กเป็นสาเหตุทั้งหมดของผล BN ปกติ

### 3.3 แยก training loss, monitoring และการเลือกโมเดล

- Cross-Entropy ต่อคลิปเทียบเท่า `-ln(p_true_class)` แล้วเฉลี่ยคลิป โดย `p_true_class` มาจาก softmax ของ logits
- `Train(eval)` และ `Dev` ใน Terminal/กราฟวัดใน eval mode หลัง epoch โดยไม่ปรับน้ำหนัก
- `train_optimization_mean_loss` คือค่าเฉลี่ยขณะฝึกที่มี Dropout และน้ำหนักเปลี่ยนระหว่าง batch เก็บแยกใน JSON
- Dev ไม่ใช้คำนวณ gradient แต่ใช้พัฒนา recipe และเลือก checkpoint จึงไม่ใช่ชุดทดสอบสุดท้าย
- ค่า loss ไม่ใช่ accuracy, EER หรือเปอร์เซ็นต์ผิด และการลด loss ไม่รับรองว่าจำนวนคลิปที่ทายถูกเพิ่มในสัดส่วนเดียวกัน
- ใช้ RNG-preserving monitoring/reload เพื่อไม่ให้การตรวจระหว่าง epochs เปลี่ยน trajectory การสุ่มของการฝึก

### 3.4 Protocol งานหลักตามเค้าโครง Ass6: ยังต้อง implement/ล็อกก่อนรัน

1. เลือก cohort และแบ่ง Train/Dev/Final Test ก่อนสร้าง TTS/augmentation โดยป้องกัน speaker/text/source/derived-file leakage
2. ใช้ pretrained Thai TTS อย่างน้อยสองระบบที่ผ่าน QC เดียวกัน กำหนดสัดส่วน TTS และ label ในการฝึก
3. Noise ใช้ SNR 10 และ 5 dB; แยก noise recordings ระหว่าง Train/Dev/Test
4. Telephone ใช้ band limitation และ G.711 encode/decode ต้องระบุย่านความถี่ sample rate, codec variant และค่าประมวลผลจริงก่อนรัน
5. Clean/Mixed ภายในโมเดลเดียวกันเริ่ม checkpoint เดียวกัน ใช้ base items/สัดส่วน label/generator ร่วมกัน และควบคุม batch/update budget ให้เทียบกันได้
6. การเลือก checkpoint ใช้ `(EER_Dev_Clean + mean(EER_Dev_Noise_10, EER_Dev_Noise_5) + EER_Dev_Telephone) / 3` ตามเกณฑ์ให้สามสภาพน้ำหนักเท่ากันในเล่ม ทั้งหมดนี้ยังไม่ใช่ selection ที่ใช้ใน pilot ปัจจุบัน
7. เลือก threshold แยกต่อ trained system จาก Dev รวมสามสภาพด้วยสัดส่วนที่กำหนดล่วงหน้า แล้วล็อกใช้กับ Test ทุกสภาพสำหรับ Precision/Recall/F1/confusion matrix และอัตราผิดพลาดสองฝั่ง
8. EER ของ Test คำนวณโดยกวาด threshold บนคะแนน Test เพื่อสรุป metric แต่ไม่ใช้ threshold จาก Test กลับไปปรับระบบ
9. ประเมินสี่สูตรบน base Test เดียวกันทุก condition รายงาน EER แยก SNR และ TTS; กำหนดการใช้ bonafide และการถ่วงผลรวมให้ชัด
10. วิเคราะห์ Dev แล้วปรับเฉพาะ Train ได้ภายใต้งบทดลองที่กำหนด ห้ามวนใช้ Test ปรับ TTS/augmentation/training หากต้องการพิสูจน์ประโยชน์ของ adaptive loop ต้องเพิ่ม controlled experiment ต่างหาก
11. Held-out TTS เป็นงานเสริมเมื่อมีทรัพยากร ต้องกัน generator นั้นออกจาก Train และ Dev จึงจะใช้ศึกษา unseen-generator performance ได้

### 3.5 ขอบเขตโค้ด inference ที่ต้องระวัง

- AASIST adapter ปัจจุบันใช้หนึ่งช่วงแรก/short repeat และโหลด pretrained ตาม config; ไม่โหลด checkpoint fine-tuned หรือ threshold ที่เลือกให้อัตโนมัติ
- RawNet2 adapter มี `all_chunks=True`/`--all-chunks`: แบ่งช่วงไม่ overlap 64,600 samples, repeat ช่วงท้ายที่สั้น และเฉลี่ย probabilities ฟีเจอร์นี้ยังไม่ใช่ policy ร่วมที่ประเมินใน pilot
- CLI เดิมของสองโมเดลมีนิยาม score/resampling/การจัดการ amplitude ต่างกันบางส่วน งานหลักต้องใช้ shared preprocessing และ score/threshold convention ที่ตรวจแล้ว ไม่เทียบค่าคะแนนดิบข้ามสองโมเดลโดยตรง
- ผลตรวจโครงสร้างแบบ read-only วันที่ 8 ตุลาคม: pretrained และ checkpoint `frozen3_my_run_01/epoch_003.pt` รับ input ตัวอย่าง 1, 2, 3, 4.0375, 6, 8 วินาทีที่ 16 kHz ได้ใน eval mode ขนาด output `(1, 2)` เป็น finite ทั้งหมด ใช้คลิป Dev ตัวอย่างตัด/วนให้ได้ขนาด ไม่ใช่ผล accuracy หรือการฝึกที่ความยาวใหม่ และไม่มี run artifact ถาวรสำหรับการตรวจนี้
- สคริปต์ฝึกปัจจุบันยัง guard ที่ 64,600 samples/16 kHz การรองรับของ network ไม่ทำให้เปลี่ยน recipe ผ่าน CLI ได้ทันที

## 4. ผลการทดลองที่ได้แล้ว: ตัวเลข metric และหลักฐาน

ทุกผลในส่วนนี้เป็น feasibility pilot ใช้ Wayu ตัวเดียว ไม่มี Noise/Telephone/Final Test และยังไม่มี EER ของงานหลัก

### 4.1 การทดลองตรวจระบบและ BatchNorm

| Run ID | วิธีทดลอง | ผลจริง | ข้อสรุปที่รองรับ |
| --- | --- | --- | --- |
| `preflight_20261007_v1` | Train 4 คลิป/1 update | Dev CE 1.594355 -> 2.112910; reload error 0 | เส้นทาง forward/backward/update/save/reload ทำงาน |
| `clean_epoch1_20261007_v1` | Train 160 / Dev 40, BN ปกติ, 1 epoch | Dev CE 1.594355 -> 4.853433; 10 updates; reload error 0 | รันได้ แต่ Dev CE แย่ลง |
| `fixed4_20261007_v1` | Train 2 real + 2 Wayu ซ้ำ, 20 updates | Train subset CE 3.375760 -> 0.002260; accuracy 50% -> 100% | จำ Train 4 คลิปได้ ไม่ใช่ unseen accuracy |
| `bn_pair_20261008_v1_train` | BN ปกติ 1 epoch ใน controlled pair | Dev CE 4.853433 จาก baseline 1.594355 | arm อ้างอิง |
| `bn_pair_20261008_v1_frozen` | Frozen BN 1 epoch ใน controlled pair | Dev CE 1.074124 จาก baseline 1.594355 | Frozen ดีกว่าในคู่ทดลองนี้ |

Fixed-4 diagnostic เปลี่ยน recipe เพื่อทดสอบความสามารถในการเรียนรู้: AdamW LR `1e-4`, weight decay 0, effective batch 4, `eval()` พร้อม autograd, Dropout ปิด, BN frozen, fixed inputs เกณฑ์ผ่านกำหนดก่อนรันเป็น accuracy 100% และ CE <= 0.1 หลังอย่างน้อย 20 updates ไม่ใช้ Dev/Test ในการตรวจนี้

BN pair ควบคุม seed/checkpoint/data/crops/order/optimizer/งบเท่ากัน เปลี่ยนเฉพาะ BN mode; Dropout เปิดเหมือนกัน มี BN 18 layers/54 buffers: โหมดปกติเปลี่ยน 54 buffers, Frozen เปลี่ยน 0 และ reload logits ตรงกัน

หลักฐาน: [BN comparison.json](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_bn_diagnostic/bn_pair_20261008_v1/comparison.json) และ [fixed-4 run.json](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_overfit_check/fixed4_20261007_v1/run.json)

### 4.2 Frozen BN สาม epochs: seed 42

Run `frozen3_20261008_v1`; เริ่ม pretrained ใหม่

| Epoch | Train evaluation CE | Dev CE |
| --- | ---: | ---: |
| 0: pretrained | 1.785548 | 1.594355 |
| 1 | 1.477809 | 1.074124 |
| 2 | 0.972610 | 0.642973 |
| 3 | 0.530635 | 0.338209 |

เลือก epoch 3 ตาม Dev CE ภายในงบ 1-3; BN buffers ไม่เปลี่ยน; checkpoint reload error 0 ทุก epoch เวลาเฉพาะช่วงจับเวลา training/evaluation/reload/plot ประมาณ 51.15 วินาทีบน RTX 3050 Ti Laptop ไม่รวม startup/audit ทั้งหมด

ผู้ใช้รันซ้ำด้วย `frozen3_my_run_01` ได้ตัวเลข curve ตรงกัน เป็น repeat ของ seed เดิม ไม่เพิ่มเป็น independent seed ที่สี่

หลักฐาน: [run.json](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_frozen_bn_curve/frozen3_20261008_v1/run.json), [กราฟ seed 42](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_frozen_bn_curve/frozen3_20261008_v1/loss_curve.png), [กราฟรอบผู้ใช้](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_frozen_bn_curve/frozen3_my_run_01/loss_curve.png)

### 4.3 ตรวจสาม training seeds บน split เดิม

Suite `seeds_20261008_v1`: ใช้ run seed 42 เดิมที่ตรวจผ่าน และฝึกใหม่จาก pretrained เฉพาะ seeds 43/44 ด้วย recipe เดิม

| Seed | Train evaluation CE หลัง epoch 3 | Dev CE หลัง epoch 3 |
| --- | ---: | ---: |
| 42 | 0.530635 | 0.338209 |
| 43 | 0.557739 | 0.338875 |
| 44 | 0.618491 | 0.404151 |
| Mean | 0.568955 | 0.360412 |
| Sample SD (`ddof=1`) | 0.044989 | 0.037881 |

Train/Dev CE ลดต่อเนื่องทุก seed ในสาม epochs; epoch 3 เป็น best Dev CE ของแต่ละ run รายงานครบทุก seed ไม่เลือกเฉพาะ winner ค่า SD แสดง training variability บน split เดิม ไม่ใช่ confidence interval หรือความแปรปรวนจากการสุ่ม cohort ใหม่

หลักฐาน: [summary.json](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_seed_stability/seeds_20261008_v1/summary.json) และ [กราฟสาม seeds](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_seed_stability/seeds_20261008_v1/seed_curves.png)

### 4.4 สิ่งที่ยังไม่มีตัวเลขให้รายงาน

- EER/accuracy/F1 บน Final Test ตาม protocol ใหม่
- ผล RawNet2 fine-tuning ใน repository นี้
- ผล Clean เทียบ Mixed หรือความทนทานต่อ Noise/Telephone
- ผลแยก demographic หรือ held-out TTS
- หลักฐานว่า Frozen BN เป็น main recipe ที่ดีที่สุด หรือว่าไม่มี overfitting

บันทึกการตรวจโค้ดล่าสุดจากการพัฒนาเมื่อ 8 ตุลาคมมี 151 tests ผ่าน เอกสารส่งต่อครั้งนี้ตรวจรายงานเดิม ไม่ได้รัน test suite หรือฝึกโมเดลซ้ำ

## 5. สิ่งที่ลองแล้วไม่เวิร์ก และเพราะอะไร

| สิ่งที่พบ | หลักฐาน/เหตุผลที่ทราบ | การตัดสินใจและสิ่งที่ยังไม่ทราบ |
| --- | --- | --- |
| MMS Thai อ่านบางคำผิด | ผู้ใช้ฟังคำว่า “โม้” เป็น “โหมด/โมด/โหวด”; ข้อความยาวมี “ชำระเงิน” ขาดเป็น “ชำเงิน” | ทดลองเตรียมข้อความเกี่ยวกับสระอำและเปลี่ยน seed; คำ “โม้” ยังผิดใน seeds 7, 123, 2026 จึงเปลี่ยนมาลอง Wayu สาเหตุภายใน model/frontend ยังไม่ได้พิสูจน์ |
| AASIST BN ปกติหนึ่ง epoch ทำ Dev แย่ลง | Dev CE เพิ่ม 1.594355 -> 4.853433 และเกิดซ้ำใน controlled BN pair | ทดลอง Frozen BN แล้วลดเหลือ 1.074124 จึงศึกษาต่อ สถิติจาก microbatch เล็กหรือ domain shift เป็นสมมติฐาน ไม่ใช่ข้อสรุปสาเหตุทั้งหมด |
| เปลี่ยน seed ไม่ได้แก้ปัญหาการออกเสียง MMS ที่พบ | คำเป้าหมายยังผิดในทุก seed ที่ลอง | ไม่ถือว่า seed เป็นปุ่มแก้ pronunciation หรือวิธีเพิ่มจำนวนผู้พูด |
| รันซ้ำโดยใช้ run-id เดิม | script ตั้งใจปฏิเสธ output directory ที่มีอยู่ | ใช้ run-id ใหม่ ไม่ลบผลเก่าหรือแก้ guard เพื่อทับงาน |

ข้อจำกัดที่ยังไม่ได้ทดลองแก้และต้องไม่รายงานเป็น “ผลล้มเหลว”:

- Wayu ตัวเดียว/voice เดียวอาจทำให้ detector เรียนรู้ร่องรอยเฉพาะ generator; ยังไม่มีการทดสอบ cross-generator
- การ repeat คลิปสั้นทำให้เกิดรอยต่อ/รูปแบบซ้ำได้ แต่ยังไม่มี controlled comparison กับ zero padding/คัดคลิปสั้นออก
- การแปลง real MP3 กับ native TTS WAV ให้เป็น canonical เดียวกันยังไม่รับรองว่ากำจัด shortcut จาก codec/bandwidth ได้
- ความเห็นว่าเสียง TTS ดู monotone/ขาดลมหายใจเป็นความเห็นจากการฟัง ไม่ได้เป็น metric หรือเกณฑ์ตัดเสียงที่ผู้ใช้อนุมัติให้บันทึกใน QC
- เคยมีปัญหา hash จาก CRLF/LF หลัง Git checkout; ใช้การตรวจ source compatibility ที่ยอมรับเฉพาะ newline conversion/การเพิ่ม seed CLI ตามกรณีที่ตรวจไว้ โดย hash ของเสียงและ manifest ยังคง byte-exact อย่าแก้ historical report ให้ตรงกับโค้ดใหม่อย่างไม่มีหลักฐาน

## 6. คำแนะนำจากอาจารย์ที่ปรึกษา

แหล่งข้อมูลส่วนนี้เป็นสิ่งที่ผู้ใช้รายงานและเนื้อหาเค้าโครง ไม่มีบันทึกเสียง/บันทึกประชุมที่ยืนยันถ้อยคำของอาจารย์โดยตรง

### 6.1 คำแนะนำที่ผู้ใช้รายงานชัดเจน

- ให้ลองรัน/ลอง train โมเดลก่อน จึงเกิด pilot AASIST ตั้งแต่ smoke, fixed-4, BN comparison จนถึงสาม seeds
- ต้องทำความเข้าใจ dataset ที่นำมาใช้ แหล่งที่มา คุณสมบัติ ข้อจำกัด และขอบเขตของเสียงที่โมเดลรับ
- ต้องอธิบายทฤษฎี TTS, fine-tuning และข้อดี/ข้อจำกัดของ AASIST กับ RawNet2 ให้ได้
- เคยสอบถามเรื่องอายุ เพศ และถิ่น/สำเนียงของผู้พูดในช่วงแผน dataset เดิม ประเด็นว่าต้องมีครบในชุดหลักหรือเป็นการวิเคราะห์เสริมยังไม่มีคำยืนยันสุดท้ายในหลักฐานที่มี
- ผู้ใช้เข้าใจจากการหารือว่าควรใช้ข้อความ Common Voice สร้าง TTS แล้ว fine-tune สอง detector และเปรียบเทียบ Clean กับหลายสภาพเสียง

### 6.2 สิ่งที่เป็นแนวทางในเค้าโครง/การออกแบบของทีม ไม่ควรอ้างว่าอาจารย์สั่งทุกค่า

- TTS อย่างน้อยสองระบบ, Noise 10/5 dB, G.711 และ Dev EER selection เป็นรายละเอียดใน Ass6
- Frozen BN, microbatch 2, accumulation 8, LR `1e-5`, สาม epochs และ seeds 42/43/44 เป็นค่าที่ทีมใช้ตรวจ pilot ไม่พบหลักฐานว่าเป็นข้อกำหนดจากอาจารย์
- มีความกำกวมเดิมเรื่องการ “วนผลกลับไปสร้างเสียงใหม่” แนวทางที่บันทึกใน Ass6 ข้อ 5.6 คือใช้ Dev วิเคราะห์แล้วปรับ Train ก่อนล็อกวิธี; Test ใช้ประเมินสุดท้ายเท่านั้น
- FastSpeech 2 เป็นแหล่งทฤษฎี ไม่ใช่คำยืนยันว่าจะใช้ generator นี้จริง
- ผลตรวจ network ที่รับความยาวอื่นได้เป็น technical diagnostic ไม่ใช่เหตุผลเพียงพอให้เปลี่ยน window โดยไม่มีการเปรียบเทียบ

ประเด็นที่ควรนำไปยืนยันครั้งถัดไป: บทบาท demographic analysis, ขนาด cohort/งบเครื่อง, TTS ที่สอง, จำนวนรอบ tuning และการรวม held-out TTS เป็นงานเสริมตามทรัพยากร

## 7. งานที่ค้างอยู่ และ deadline

### 7.1 ลำดับงานถัดไป

| ลำดับ | งาน | ผลส่งมอบ/เกณฑ์เสร็จ | ผู้รับผิดชอบตามการแบ่งงานปัจจุบัน |
| --- | --- | --- | --- |
| 1 | ทำ protocol ให้เป็นฉบับเดียวกัน | ยืนยัน SNR, G.711 profile, selection/threshold, cohort, split, QC, tuning/compute budget และข้อจำกัด | ผู้ใช้ + เพื่อน + อาจารย์ |
| 2 | คัดข้อมูลหลักและแบ่ง split | immutable manifests; ตรวจ speaker/text/source/derived overlap; จำนวน/ชั่วโมงต่อชุด | งานข้อมูลร่วม |
| 3 | เลือก TTS ตัวที่สอง | ทดลองข้อความ Train, ตรวจคุณภาพ/รุ่น/สิทธิ์/ต้นทุน และกำหนดสัดส่วนก่อนสร้างจริง | งานข้อมูลร่วม |
| 4 | ให้ RawNet2 ผ่าน pilot | trainer ใช้ canonical/labels/windows ร่วม ตรวจ update/save/reload และผล Dev | เพื่อนฝั่ง RawNet2 |
| 5 | สร้าง TTS หลักและ QC | provenance/QC/reject reasons ครบ; split สืบทอดจากรายการต้นฐาน | งานข้อมูลร่วม |
| 6 | ทำ Noise/Telephone pipeline | noise pools แยก split, SNR ถูกต้อง, G.711 reproducible, Dev/Test condition manifests คงที่ | งานข้อมูลร่วม |
| 7 | เพิ่ม main trainers | checkpoint/resume/selection/score convention/logging ที่ตรวจแล้ว คุมงบ Clean/Mixed | แยก AASIST/RawNet2 |
| 8 | ฝึก/เลือกบน Dev | ผลสี่สูตร; ใช้เกณฑ์ Dev EER ตาม protocol; รายงานทุก seed ที่กำหนด | ทั้งสองฝั่ง |
| 9 | ล็อกแล้วประเมิน Final Test | EER แยก condition/TTS พร้อม fixed-threshold metrics และข้อจำกัด | ทั้งสองฝั่ง |
| 10 | ทำต้นแบบและรายงาน | โหลด checkpoint/threshold ที่เลือกจริง แสดงผลไฟล์เสียงและข้อจำกัด | ทีม |

งานแรกที่ทำต่อได้: ตรวจจำนวนคลิป/รหัสผู้พูด/ข้อความที่ผ่าน QC เพื่อกำหนด cohort และตกลง protocol จากนั้นแบ่งข้อมูลก่อนสร้างเสียงจำนวนมาก ไม่จำเป็นต้องรัน pilot 1-10 ซ้ำทั้งหมด

ข้อมูล pilot และโดยเฉพาะ Dev pilot ถูกใช้พัฒนา recipe/ตรวจเสียงแล้ว หากสร้าง Final Test ใหม่ ต้องกันรายการ ผู้พูด และข้อความที่ใช้พัฒนาเหล่านี้ออกตามนโยบายที่ล็อกไว้ ห้ามเปลี่ยนชื่อ Dev เดิมเป็น Test แล้วอ้างว่าเป็นการทดสอบอิสระ

### 7.2 ความไม่ตรงกันในเอกสารที่ต้องสะสาง

| ประเด็น | สถานะปัจจุบัน | สิ่งที่ต้องทำ |
| --- | --- | --- |
| Noise SNR | workflow เก่าเสนอ 0/10/20 dB; Ass6 ระบุ 10/5 dB | ใช้ Ass6 เป็นแผนอ้างอิงล่าสุดในการหารือ แล้วอัปเดต protocol/docs/config ให้ตรงกันก่อน implement |
| Checkpoint selection | pilot ใช้ Dev CE; main ใน Ass6 ใช้ mean Dev EER สามสภาพ | สร้าง main selector แยก ไม่เปลี่ยนผล pilot ย้อนหลัง |
| Dataset/generators | pilot 200 คลิป Wayu เดียว ไม่มี Test | สร้าง version งานหลักใหม่และ TTS >= 2 ระบบ |
| Fixed window | pilot 64,600 samples/repeat; Ass6 ไม่ล็อกเลขนี้ | กำหนด policy สำหรับ main พร้อมเหตุผลและวิธีใช้ร่วมกัน |
| Decision log เก่า | ยังมีหัวข้อรอยืนยัน release/TTS-vs-cloning จากช่วงต้น | ตรวจรายการที่ทราบแล้วกับสิ่งที่ต้องให้อาจารย์ยืนยัน แก้ตามหลักฐานใหม่ |

ไฟล์ workflow เก่าคือ [COMMON_VOICE_PROJECT_WORKFLOW_TH.md](D:/KKU_files/year3_semester1/CP353761/project/docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md) มีคำสั่ง/จำนวน/งบที่เสนอไว้ซึ่งยังไม่ implement อย่ารันหรืออ้างว่าทำแล้วตามข้อความแผนเพียงอย่างเดียว

### 7.3 Deadline และเวลา

- ยังไม่มีวันส่งงานหลัก/วันสอบ/วัน progress ถัดไปที่ยืนยันในข้อมูลที่ตรวจ ณ 14 ตุลาคม 2026
- เค้าโครงมีแผนระยะเวลา 16 สัปดาห์ แต่ยังแปลงเป็นวันที่จริงไม่ได้จากหลักฐานนี้ ต้องยืนยันวันเริ่มและกำหนดส่งกับผู้ใช้/อาจารย์
- คำขอเตรียม progress “พรุ่งนี้” ในช่วง 8-10 ตุลาคมเป็นบริบทที่ผ่านมา ไม่ใช่ deadline ใหม่ของเอกสารนี้
- อย่าตั้งวันที่สมมติหรือเริ่มขยายงานใหญ่โดยถือว่ามีงบ GPU/เวลามากพอ ควรยืนยันจำนวนวันและทรัพยากรก่อนกำหนด cohort/จำนวน seeds

### 7.4 สภาพแวดล้อมและจุดเริ่มทำงานสำหรับผู้ช่วยใหม่

เครื่อง pilot: Windows, Python หลัก 3.12.4, PyTorch `2.11.0+cu128`, NVIDIA RTX 3050 Ti Laptop GPU 4 GB ตาม run reports

- `.venv` หลักใช้ EDA/audio preparation/detector training
- `.venv-wayu` เป็น environment แยกสำหรับ TTS (Python 3.11, PyTorch CPU และ dependencies ที่ pin ไว้) ไม่คัดลอกหรืออัปเกรดรวมกับ environment หลัก
- Python ที่ `.venv-wayu` อ้างอิงอยู่ใต้ `tmp/wayu-python` อย่าลบโฟลเดอร์นี้เป็น cleanup ทั่วไป
- ผู้ใช้ต้องการทำทีละขั้น มีคำอธิบายและผลตรวจที่ดูได้ ต้องบอกได้ว่าโค้ดส่วนไหนมาจาก upstream และส่วนไหนเขียนเพิ่ม
- ผู้ใช้ commit/push เอง ไม่ใช้ branch prefix `codex/`; ถ้ามีงาน code ใหม่ให้ใช้ชื่อ feature ที่สื่อความหมายและตรวจ working tree ก่อน
- อย่าทับ data, pretrained, historical runs หรือ ZIP ส่งต่อ เลือก run-id ใหม่ทุกครั้ง ไม่มี resume ใน trainer pilot นี้
- ผลจริง/เสียง/TSV/CSV/weights/ZIP/executed notebooks ถูก ignore โดย Git; README/`.gitkeep` ใช้ให้เห็นโครงสร้าง การ clone/pull จึงไม่ได้ข้อมูลจริง

| จุดเริ่ม/ส่วนงาน | ตำแหน่ง |
| --- | --- |
| สถานะ pilot | [Pilot README](D:/KKU_files/year3_semester1/CP353761/project/experiments/pilot/README.md) |
| พื้นที่งานหลักที่ยังเป็นแผน | [Research README](D:/KKU_files/year3_semester1/CP353761/project/experiments/research/README.md) |
| Notebook EDA/TTS/canonical | [Pilot notebooks](D:/KKU_files/year3_semester1/CP353761/project/experiments/pilot/notebooks) |
| สคริปต์ฝั่งผู้ใช้ | [AASIST scripts](D:/KKU_files/year3_semester1/CP353761/project/experiments/pilot/scripts/aasist) |
| พื้นที่ฝั่งเพื่อน | [RawNet2 scripts](D:/KKU_files/year3_semester1/CP353761/project/experiments/pilot/scripts/rawnet2) |
| การเตรียมเสียงร่วม | [cvtts helpers](D:/KKU_files/year3_semester1/CP353761/project/src/thai_spoof/cvtts) |
| Loader/BN/learning curve/seed audit | [pilot helpers](D:/KKU_files/year3_semester1/CP353761/project/src/thai_spoof/pilot) |
| ผลที่ต้องเก็บไว้ | [pilot results](D:/KKU_files/year3_semester1/CP353761/project/results/pilot) |
| วิธีส่งข้อมูลให้เพื่อน | [TEAM_HANDOFF_TH.md](D:/KKU_files/year3_semester1/CP353761/project/docs/TEAM_HANDOFF_TH.md) |

โค้ดที่ทีมเพิ่มครอบคลุม EDA/selection/splits, TTS generation/provenance/QC, canonical audio, strict loader/window policy, detector adapters, training diagnostics, Frozen BN/seeds, tests และคู่มือ ส่วน network AASIST เป็น upstream และ RawNet2 เป็น implementation ที่นำมาจาก repository ฝั่งเพื่อน ไม่ได้ออกแบบสถาปัตยกรรมใหม่

คำสั่งที่มีอยู่จริงสำหรับทดลองซ้ำจาก project root (ใช้ run-id ที่ยังไม่มี):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments\pilot\scripts\aasist\train_aasist_frozen_bn.py --run-id frozen3_handoff_01 --seed 42 --device cuda
```

Trainer นี้รับ `--run-id`, `--seed`, `--device` เท่านั้น; ยังไม่มี `--epochs`, `--lr`, `--batch-size` ค่าเหล่านั้นผูกกับ config/guards/รายงานในโค้ด หากต้องทำ parameter experiments ควรเพิ่ม configuration ที่ตรวจแล้วและตั้ง experiment version ใหม่

ผลใหม่สร้างในโฟลเดอร์ชื่อ run-id ใต้ [aasist_frozen_bn_curve](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/aasist_frozen_bn_curve) มี `run.json`, `learning_curve.json`, `training_log.json`, `scores.csv`, `epoch_001.pt` ถึง `epoch_003.pt`, `selection.json`, `loss_curve.png` ไม่มีการแทน pretrained หรือการเลือก checkpoint เข้า CLI inference อัตโนมัติ

ZIP ส่งเพื่อนมีอยู่แล้ว: [cvtts_pilot_v1_for_rawnet2_20261007.zip](D:/KKU_files/year3_semester1/CP353761/project/results/pilot/share/cvtts_pilot_v1_for_rawnet2_20261007.zip) ประมาณ 61.96 MiB มี pilot payload 463 ไฟล์และ original MP3 100 ไฟล์ รวมข้อมูล 563 ไฟล์ พร้อม checksum/คู่มือ ไม่รวม weights/environment/source code/full Common Voice ภายหลังแตกที่ project root ให้รัน `python _pilot_handoff/verify_package.py` ตามคู่มือ ไม่จำเป็นต้องสร้างแพ็กใหม่เพียงเพราะเพิ่มโค้ดฝึก

เมื่อเริ่มงานต่อ ให้ตรวจสถานะจริงก่อน แล้วจัด protocol ให้ชัดก่อนขยาย dataset/จำนวน epochs/seeds สิ่งที่ต้องรักษาคือข้อมูลไม่รั่วไหล การเปรียบเทียบยุติธรรม provenance ทำซ้ำได้ และเล่ม/โค้ด/ผลรายงานอธิบายวิธีเดียวกัน
