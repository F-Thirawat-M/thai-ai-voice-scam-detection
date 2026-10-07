# แผนงานหลักและคู่มือส่งต่องาน: Common Voice → Thai TTS → AASIST / RawNet2

เริ่มจัดทำ: 2 ตุลาคม 2026 · ตรวจทานล่าสุด: 3 ตุลาคม 2026 · ฉบับ: ร่าง protocol v1 · สถานะ: แผนสำหรับตกลงร่วมกันและใช้พัฒนาระบบ ยังไม่ใช่ผลทดลอง

**อัปเดตการจัดหมวด 7 ตุลาคม 2026:** ถ้าทำงานต่อจากปัจจุบันให้เปิด [Pilot README](../experiments/pilot/README.md) ก่อน มี smoke/overfit ที่ทำแล้ว ส่วนงานวิจัยจริงแยก [Research README](../experiments/research/README.md) เอกสารยาวนี้เป็นแผน main experiment; สถานะที่บันทึกตอนร่างไม่ได้แทนสถานะ pilot ปัจจุบัน และคำสั่ง proposed ยังไม่ใช่คำสั่งพร้อมรัน

> **ให้อ่านไฟล์นี้ก่อนเริ่มงานใหม่** ทิศทางปัจจุบันคือใช้ Common Voice ภาษาไทยเป็นแหล่งเสียงมนุษย์และข้อความ แล้วสร้างเสียงสังเคราะห์ด้วย TTS เพื่อเปรียบเทียบ AASIST กับ RawNet2 ภายใต้การฝึกแบบ Clean และ Clean + Noise + Telephone ผู้ใช้ให้ปรับโครงสร้างและลบข้อมูล/โค้ด/แผน SEA-Spoof และ Typhoon ที่เลิกใช้แล้วเมื่อ 3 ตุลาคม 2026 ไม่ต้องนำกลับมาเป็น dependency ของ workflow ใหม่ ดู [โครงสร้างปัจจุบัน](PROJECT_STRUCTURE_TH.md) และ [รายการ cleanup](CLEANUP_2026-10-03.md)
>
> เอกสารนี้แยก “ข้อเท็จจริงที่ตรวจใน repository” ออกจาก “ข้อเสนอที่จะพัฒนา” คำสั่งของ pipeline ใหม่ในส่วน 20 **ยังไม่มีให้รันจนกว่าจะเขียนระบบตามแผน** ห้ามรายงานว่าดาวน์โหลด สร้างเสียง ฝึก หรือประเมินสำเร็จเพียงเพราะมีแผนนี้

## สารบัญ

1. [เริ่มจากอะไร และเข้าใจโครงงานอย่างไร](#s01)
2. [ขอบเขตและเรื่องที่ต้องยืนยัน](#s02)
3. [สถานะโค้ดและสิ่งที่นำกลับมาใช้ได้](#s03)
4. [ภาพรวม workflow และการทดลอง](#s04)
5. [ข้อตกลง protocol และค่าตั้งต้น](#s05)
6. [โครงสร้างไฟล์และการแบ่งงาน](#s06)
7. [Phase 0: ตกลงโจทย์ ตรวจเครื่อง และล็อกสิ่งแวดล้อม](#s07)
8. [Phase 1: สำรวจและคัด Common Voice](#s08)
9. [Phase 2: แบ่งข้อมูลและป้องกันข้อมูลรั่ว](#s09)
10. [Phase 3: ทดลองและเลือก TTS](#s10)
11. [Phase 4: สร้างเสียงสังเคราะห์และตรวจคุณภาพ](#s11)
12. [Phase 5: เตรียมเสียงและจำลอง condition](#s12)
13. [Phase 6: สร้างระบบฝึกและประเมินที่ใช้ร่วมกัน](#s13)
14. [Phase 7: Fine-tune และเลือก checkpoint](#s14)
15. [Phase 8: Final Test และวิเคราะห์ผล](#s15)
16. [Phase 9: รายงานและการส่งมอบ](#s16)
17. [Data contracts: ฟิลด์ที่ต้องเก็บ](#s17)
18. [Quality gates และรายการทดสอบ](#s18)
19. [เครื่องส่วนตัว / Colab / พื้นที่ / การกู้คืน](#s19)
20. [คำสั่งที่มีแล้วและคำสั่งที่ต้องสร้าง](#s20)
21. [แผนงานย่อยสำหรับทีมและ AI ผู้รับช่วง](#s21)
22. [คำถามที่พบบ่อยและคำอธิบายให้อาจารย์](#s22)
23. [แหล่งอ้างอิงและข้อจำกัด](#s23)

<a id="s01"></a>
## 1. เริ่มจากอะไร และเข้าใจโครงงานอย่างไร

### 1.1 สิ่งแรกที่ต้องทำ

**ยังไม่เริ่ม fine-tune หรือสร้างเสียงจำนวนมาก** ให้ทำตามลำดับนี้ก่อน:

1. ส่งส่วน 1–5 ให้เพื่อนอ่าน แล้วตกลงความเข้าใจเดียวกัน
2. ขอให้อาจารย์ยืนยันเรื่องที่ยังไม่ชัดในส่วน 2.2 โดยเฉพาะการวนกลับไปปรับ TTS และขอบเขตอายุ/เพศ/ถิ่น
3. ระบุว่า Common Voice ที่มีเป็น release ใด ภาษาใด ได้มาจากที่ใด และมีไฟล์เสียงครบตาม metadata หรือไม่ อย่าอนุมาน release จากจำนวนแถวอย่างเดียว
4. สร้าง audit แบบอ่านอย่างเดียวและรายงานความพร้อมข้อมูล
5. ออกแบบ split ก่อนสร้างเสียงปลอม จากนั้นทดลอง TTS กับข้อความชุดเล็กจาก Train เท่านั้น
6. เมื่อ pilot ผ่าน จึงล็อก protocol แล้วค่อยสร้างข้อมูลหลักและระบบฝึก

งานข้อ 3–4 และการอ่านทฤษฎีทำระหว่างรอคำตอบอาจารย์ได้ แต่ไม่ควรลงทุนสร้างเสียงหลักทั้งหมดก่อนเลือก TTS และวิธีแบ่งข้อมูล

### 1.2 โครงงานนี้ทำอะไร

เรากำลังสร้าง **ระบบตรวจจับเสียงพูดสังเคราะห์ภาษาไทย** และศึกษาว่า การ fine-tune ด้วยเสียงหลายสภาพแวดล้อมช่วยให้ตรวจจับเสียงได้ดีขึ้นเมื่อมีเสียงรบกวนหรือผ่านช่องสัญญาณโทรศัพท์จำลองหรือไม่

- เสียงมนุษย์จริง: ใช้คลิปภาษาไทยของ Common Voice ตามเกณฑ์คัดเลือก
- เสียงปลอม: ใช้ข้อความที่เชื่อมกับคลิปดังกล่าวไปสร้างเสียงใหม่ด้วยโมเดล Text-to-Speech หรือ TTS
- ตัวสร้างเสียง: TTS ที่ผ่านการฝึกมาแล้ว ไม่ใช่ AASIST หรือ RawNet2
- ตัวตรวจจับ: AASIST และ RawNet2 ที่นำมา fine-tune ให้แยก `bonafide` กับ `spoof`
- สิ่งที่เปรียบเทียบหลัก: ตัวตรวจจับแต่ละตัวเมื่อฝึกด้วย Clean เทียบกับ Clean + Noise + Telephone
- สิ่งที่ไม่ได้ทำโดยอัตโนมัติ: สร้าง TTS จากศูนย์, clone เสียงเจ้าของคลิป, ตรวจเจตนาหลอกลวง, หรือยืนยันตัวบุคคล

**การใช้ข้อความเดียวกับเสียงมนุษย์ไม่ได้ทำให้เสียง TTS เป็นเสียงของคนคนนั้น** ถ้าใช้ TTS แบบเสียงสำเร็จรูป เรากำลังสร้างเสียงสังเคราะห์ที่พูดข้อความเดียวกัน ไม่ใช่เลียนแบบตัวตนเจ้าของเสียง

### 1.3 คำถามวิจัย

- RQ1: หลัง fine-tune ด้วยข้อมูลที่เตรียมไว้ AASIST และ RawNet2 มี EER เท่าใดในแต่ละ condition?
- RQ2: ภายในตัวตรวจจับเดียวกัน การฝึก Mixed ช่วยลด EER บน Noise และ Telephone เทียบกับฝึก Clean หรือไม่ และกระทบ Clean อย่างไร?
- RQ3 — ส่วนเสริมที่แนะนำถ้าทำได้: โมเดลตรวจจับเสียงจาก TTS ที่ไม่ได้ใช้ในการ fine-tune/เลือก checkpoint ของโครงงานได้ดีเพียงใด?

ยังไม่ตั้งสมมติฐานเป็นผลสรุปว่า Mixed ต้องดีกว่าเสมอ หากผลไม่ดีขึ้น แต่ protocol ถูกต้องและวิเคราะห์สาเหตุได้ ก็เป็นผลวิจัยที่รายงานได้

<a id="s02"></a>
## 2. ขอบเขตและเรื่องที่ต้องยืนยัน

### 2.1 ขอบเขตหลักที่ใช้วางแผนฉบับนี้

| ประเด็น | ขอบเขตฉบับร่างนี้ |
| --- | --- |
| ภาษา | เสียงพูดภาษาไทย จาก Common Voice release ที่จะตรวจยืนยัน |
| ประเภทเสียงปลอม | เสียง TTS จากข้อความ ไม่รวม replay, การตัดต่อทุกประเภท หรือ voice conversion โดยปริยาย |
| TTS | อย่างน้อย 2 ระบบที่ผ่าน pilot และตรวจสิทธิ์แล้ว ใช้ pretrained weights |
| ตัวตรวจจับ | AASIST และ RawNet2 แยก implementation / checkpoint / training run |
| แขนการฝึก | Clean-only และ Mixed: Clean + Noise + Telephone |
| การเติม condition | ทำกับทั้งเสียงมนุษย์และเสียง TTS อย่างสมดุล |
| ข้อมูลประเมิน | Train / Dev / Final Test ที่แยกไว้ก่อน synthesis และ augmentation |
| Metric หลัก | EER ต่อ condition พร้อมความผิดพลาดที่ threshold เลือกจาก Dev |
| อายุ เพศ ถิ่น | วิเคราะห์เสริมได้เมื่อมีข้อมูลเพียงพอ ยังไม่เป็นเงื่อนไขหลักของทุกตัวอย่าง |
| SEA-Spoof / Typhoon Isan | นำออกจาก workflow และลบ local datasets/EDA/pipelines ตามคำขอแล้ว; source ที่เคย commit ดูย้อนหลังได้ใน Git |
| ผลใช้งานจริง | ระบบทดลอง ไม่อ้างว่าใช้ตัดสินการหลอกลวงหรือพิสูจน์เสียงปลอมได้เด็ดขาด |

### 2.2 เรื่องที่ต้องถามอาจารย์/ตกลงกับเพื่อน

จดคำตอบลง `docs/decisions/CVTTS_DECISIONS.md` เมื่อเริ่ม implementation พร้อมวันที่และผู้ยืนยัน:

1. ใช้ “TTS จากข้อความ” เพียงพอหรือจำเป็นต้องทำ voice cloning ด้วย? ถ้าต้อง clone ต้องเพิ่มการตรวจสิทธิ์เสียงอ้างอิงและ protocol ใหม่
2. งานหลักต้องการเปรียบเทียบ Clean กับ Mixed แบบการทดลองคงที่ หรือจำเป็นต้องมีวงจรสร้างเสียงใหม่ตามข้อผิดพลาดของ detector?
3. ถ้ามีวงจรปรับปรุง ยืนยันว่าปรับจาก **Dev ไม่ใช่ Final Test** และกำหนดงบ/จำนวนรอบล่วงหน้า
4. อายุ เพศ และถิ่นเป็นเพียงการอธิบายชุดข้อมูล หรือเป็นคำถามวิจัยหลักที่ต้องวัดรายกลุ่ม?
5. ต้องทดสอบ TTS ที่ไม่เคยใช้ fine-tune ในโครงงานด้วยหรือไม่? แนะนำให้มี แต่ขึ้นกับความพร้อมของระบบสร้างเสียง
6. Telephone หมายถึง narrowband จำลองตามส่วน 12 หรืออาจารย์ต้องการบันทึกผ่านโทรศัพท์/เครือข่ายจริง?
7. ยอมรับจำนวนข้อมูลและงบ compute ตาม pilot ได้หรือมีขั้นต่ำที่กำหนด?
8. น้ำหนักตั้งต้น AASIST/RawNet2 มาจากการฝึกคนละชุด/recipe ได้หรือไม่? ถ้าใช้ของเดิม ต้องรายงานว่าเปรียบเทียบ **ระบบ fine-tuned สองระบบ** ไม่แยกผลของ architecture อย่างบริสุทธิ์

**ค่าเริ่มต้นระหว่างรอยืนยัน:** ใช้การทดลองคงที่ ไม่สร้าง adaptive loop และยังไม่ใช้ voice cloning ห้ามเขียนว่าอาจารย์อนุมัติแล้ว

### 2.3 ถ้าภายหลังต้องทำวงจรปรับปรุง

แยกเป็นการทดลองเพิ่ม ไม่ปะปนกับสี่แขนหลัก:

1. ฝึกจาก Train รุ่นเริ่มต้น → ตรวจ Dev → จัดหมวดข้อผิดพลาด
2. ปรับ generator/voice/พารามิเตอร์หรือสัดส่วนการสร้างเสียง **ใน Train** ตามกติกาที่ประกาศไว้
3. ฝึกใหม่ตามงบเท่ากัน พร้อมกลุ่มเปรียบเทียบที่ไม่ปรับข้อมูล
4. จำกัดรอบล่วงหน้า เช่น ไม่เกิน 2 รอบ ใช้ Dev เดิมอย่างระวังและบันทึกทุกการลอง
5. เลือกวิธีสุดท้ายจาก Dev แล้วจึงเปิด Final Test เพียงหลังจบการพัฒนา

ถ้าดู Final Test แล้วนำข้อผิดพลาดไปปรับระบบ ชุดนั้นกลายเป็นข้อมูลที่ใช้พัฒนาแล้ว ผลรอบต่อไปต้องระบุว่า exploratory หรือหาชุด Final Test ใหม่ที่ยังไม่ใช้เลือกวิธี ไม่ใช้คำว่า “test อิสระ” ต่อไปโดยไม่อธิบาย

<a id="s03"></a>
## 3. สถานะโค้ดและสิ่งที่นำกลับมาใช้ได้

ส่วนนี้ปรับตาม repository หลัง cleanup 3 ตุลาคม 2026 ไม่ใช่การยืนยันว่าเครื่องอื่นมีไฟล์เหมือนกัน

| ส่วน | มีแล้ว | งานที่ต้องเพิ่ม/ปรับ |
| --- | --- | --- |
| AASIST | source ทางการใน `external/aasist/`, wrapper และ checkpoint ตั้งต้น | training adapter ที่ใช้ gradient และโหลด checkpoint ที่ฝึกใหม่ได้ |
| RawNet2 | wrapper, model, ตัวเตรียม checkpoint ทางการ | training adapter / config / loss ที่ตรง output |
| CLI ปัจจุบัน | `infer`, `evaluate`, เลือก `--model` ได้ | workflow Common Voice, TTS, train, scoring และ threshold แยก Dev/Test |
| Audio | โหลด mono/resample/crop-repeat สำหรับ inference | shared preprocessing ที่ให้ทั้งสองโมเดลรับ tensor และ condition เดียวกัน |
| Metrics | EER แบบจุด ROC ใกล้ FAR=FRR และค่าประเมินอื่น | ประกาศ EER method, fixed Dev threshold, reject nonfinite, regression tests |
| Dataset EDA | มี Common Voice notebook แบบง่าย ใช้ pandas ดูข้อมูลและเสียงตัวอย่าง; EDA เก่าถูกลบแล้ว | full waveform QC / project split / synthesis lineage ยังต้องพัฒนา |
| Training workflow ใหม่ | ยังไม่มี | ต้องสร้างและทดสอบ ไม่ใช่เพียงเพิ่ม CLI argument |

ไฟล์ที่ผู้พัฒนาควรอ่านก่อนแก้:

- `src/thai_spoof/cli.py`: เส้นทางคำสั่งปัจจุบัน
- `src/thai_spoof/metrics.py`: การแปลง label และคำนวณคะแนน
- `src/thai_spoof/prediction.py`: นิยามคะแนน/ผลทำนาย
- `src/thai_spoof/aasist/audio.py`: การเตรียมเสียงที่ AASIST ใช้อยู่
- ตรวจตำแหน่ง `detector.py`, `model.py`, config ของแต่ละโมเดลด้วย `rg --files src` ไม่เดาชื่อโฟลเดอร์
- `external/aasist/main.py`, `external/aasist/data_utils.py`, `external/aasist/config/AASIST.conf`: อ่านเพื่อเข้าใจต้นฉบับ ไม่คัด training loop มาใช้โดยไม่ปรับ
- `scripts/check_environment.py`, `pyproject.toml`, `.gitignore`, `tests/`

ข้อควรระวังที่พบ:

1. wrapper ทำนายใช้ inference mode จึงนำ `predict()` ไปฝึกโดยตรงไม่ได้ ต้องเรียก network ผ่าน training adapter
2. AASIST และ RawNet2 ปัจจุบันใช้ resampler/การจัดการ peak และสเกลคะแนนต่างกัน ต้องทำ shared pipeline ก่อนเปรียบเทียบ
3. `evaluate` เดิมเลือก threshold จากชุดที่ส่งเข้าไป จึงยังไม่เหมาะกับการรายงาน fixed-threshold Final Test ตามแผนนี้
4. AASIST ต้นฉบับมีทางเลือกประเมิน evaluation set ระหว่าง training และ class weights สำหรับข้อมูลเดิม ห้ามนำมาใช้กับ Final Test/สัดส่วน label ใหม่โดยอัตโนมัติ
5. random crop ของต้นฉบับที่ตรวจมีกรณีขอบเขตความยาวต้องระวัง ให้สร้างฟังก์ชันที่ทดสอบกรณี `length == 64600` และเลือกจุดเริ่มสุดท้ายได้
6. `.gitignore` ปรับให้ครอบคลุม data/raw, data/processed, sample files, EDA outputs, `.venv-*` และ `.env` แล้ว ให้เก็บ manifest จริงใต้ dataset version และตรวจ `git check-ignore` ก่อนเพิ่ม artifact ชนิดใหม่
7. ไม่ควรรัน `scripts/setup.ps1` ซ้ำโดยไม่อ่าน เพราะมีขั้นตอนติดตั้ง/อัปเกรด dependency และดึง upstream ซึ่งอาจเปลี่ยน environment ที่ใช้งานได้อยู่

<a id="s04"></a>
## 4. ภาพรวม workflow และการทดลอง

```text
ยืนยันคำถามวิจัย + release/สิทธิ์ข้อมูล + งบเครื่อง
    ↓
Common Voice Thai: metadata audit + audio QC + ตรวจข้อมูลซ้ำ
    ↓
เลือก cohort → แบ่ง Train / Dev / Final Test → บันทึก split แบบคงที่
    ↓
Pilot TTS ด้วยข้อความ Train → เลือก G1/G2 (+ G3 held-out ถ้าพร้อม)
    ↓
สร้าง TTS แยกตาม split ของข้อความต้นทาง → ตรวจคุณภาพ → ล็อก base manifests
    ↓
shared audio: mono 16 kHz → window 64,600 samples → condition
    ├── Train Clean → AASIST / RawNet2
    └── Train Mixed (Clean หรือ Noise หรือ Telephone) → AASIST / RawNet2
                ↓
Dev: เลือก checkpoint + threshold (ปรับได้เฉพาะขั้นพัฒนา)
                ↓
ล็อก protocol / configs / checkpoints / thresholds
                ↓
Final Test: Clean / Noise 20,10,0 dB / Telephone
                ↓
EER + fixed-threshold errors + สถิติ + วิเคราะห์ + รายงาน
```

### 4.1 การทดลองหลักสี่แบบ

| Run family | ตัวตรวจจับ | ข้อมูลที่ใช้ fine-tune | สิ่งที่ใช้เหมือนกัน |
| --- | --- | --- | --- |
| A-C | AASIST | Clean | base Train, label sampling, init ของ AASIST, งบฝึกของ AASIST |
| A-M | AASIST | Mixed | เหมือน A-C ยกเว้น condition ของ waveform |
| R-C | RawNet2 | Clean | base Train, label sampling, init ของ RawNet2, งบฝึกของ RawNet2 |
| R-M | RawNet2 | Mixed | เหมือน R-C ยกเว้น condition ของ waveform |

ทุกแบบประเมินบน Test รายการเดียวกันและ condition เดียวกัน ไม่ใช่ให้ Clean model เจอเฉพาะ Clean test แล้ว Mixed model เจอเฉพาะ Noise test

- เป้าหมาย: 3 training seeds ต่อแบบ = 12 fine-tune runs หากทำได้
- Pilot ใช้ seed เดียวและข้อมูลน้อยเพื่อทดสอบระบบ ไม่ใช้สรุปผลหลัก
- ถ้างบไม่พอ 3 seeds ต้องตกลงลดก่อนดู Test และรายงานข้อจำกัด ไม่เลือกเฉพาะ seed ที่ดีที่สุด
- ประเมิน checkpoint pretrained เดิมของแต่ละโมเดลบนชุดเดียวกันได้ เป็น reference เพิ่ม ไม่แทนผล fine-tune
- สี่แบบนี้ตอบผลของ **training condition** แต่ยังไม่พิสูจน์ว่าหลาย TTS ดีกว่า TTS เดียว หรือการปรับ pitch ช่วยลด overfitting หากต้องการอ้างต้องเพิ่ม ablation แยก

<a id="s05"></a>
## 5. ข้อตกลง protocol และค่าตั้งต้น

ค่าต่อไปนี้เป็น **ข้อเสนอเริ่มต้นสำหรับ pilot** ไม่ใช่ค่าที่ทดสอบแล้วว่าเหมาะที่สุด ต้องยืนยันและล็อกก่อนประเมิน Final Test

| รายการ | ค่าเสนอ | เงื่อนไข |
| --- | --- | --- |
| Base labels | `spoof=0`, `bonafide=1` | ตรวจ class order ของ checkpoint จริงทุกตัว |
| Split target | Train 80% / Dev 10% / Test 10% | ระดับผู้พูด/กลุ่มก่อนคัดจำนวน ไม่รับประกันจำนวนแถวตรงเปอร์เซ็นต์ |
| Split seed | 20261002 | ห้ามเปลี่ยนเพียงเพื่อให้คะแนนดูดี |
| Training seeds | 13, 37, 73 | บันทึก Python / NumPy / Torch / sampler RNG |
| Audio | mono, 16,000 Hz, float32 ในหน่วยความจำ | เก็บ original/native audio แยกไว้ |
| Input window | 64,600 samples = 4.0375 วินาที | ความยาว input ต่อครั้ง ไม่ใช่ความยาวไฟล์สูงสุด |
| Train crop | สุ่มตำแหน่ง; สั้นกว่านี้ repeat | crop seed เท่ากันระหว่าง Clean/Mixed คู่เดียวกัน |
| Dev/Test crop | ช่วงแรก; สั้นกว่านี้ repeat | ห้ามสุ่มใหม่แต่ละครั้ง |
| Mixed probabilities | Clean 1/3, Noise 1/3, Telephone 1/3 | เลือกหลังสุ่ม base sample; ไม่ผูกกับ label/generator |
| Train noise SNR | สุ่มจาก 0, 10, 20 dB ด้วยโอกาสเท่ากัน | ใช้ noise pool ของ Train เท่านั้น |
| Dev selection conditions | Clean, Noise 10 dB, Telephone | ใช้ค่าเฉลี่ย EER ของ 3 condition น้ำหนักเท่ากัน |
| Final Test conditions | Clean, Noise 20/10/0 dB, Telephone | เป็น 5 condition; ทุกแบบใช้ base cohort เดียวกัน |
| Telephone | narrowband profile ตามส่วน 12.4 | ไม่อ้างว่าแทนโทรศัพท์ทุกระบบ |
| Noise+Telephone พร้อมกัน | ยังไม่รวมใน v1 | หากเพิ่มต้องตั้งชื่อ condition และแผนไว้ล่วงหน้า |
| TTS pitch/speed sweep | ยังไม่ทำในงานหลัก | preset voice/seed policy ที่กำหนดไว้เท่านั้น |
| Final decision threshold | เลือกจาก Dev แยกต่อ run | คงค่าเดียวข้ามทุก Test condition ของ run นั้น |

### 5.1 งบข้อมูลตัวอย่างสำหรับเริ่มประเมินความเป็นไปได้

**ไม่ใช่จำนวนข้อมูลที่มีแล้วหรือขั้นต่ำทางสถิติ** ตัวอย่างเป้าหมาย core cohort หลัง QC:

| Split | ข้อความไม่ซ้ำ / คลิปจริง | TTS จาก G1 | TTS จาก G2 | Base clips รวม |
| --- | ---: | ---: | ---: | ---: |
| Train | 6,000 | 6,000 | 6,000 | 18,000 |
| Dev | 1,000 | 1,000 | 1,000 | 3,000 |
| Final Test | 1,000 | 1,000 | 1,000 | 3,000 |

- หนึ่งข้อความเลือกเสียงจริงต้นทางหนึ่งคลิปด้วย seed คงที่ แล้วสร้างเสียง G1 และ G2 อย่างละหนึ่งคลิป จึงติดตามคู่ข้อความได้ง่าย
- จำนวนเป้าหมายเป็นการคัดย่อย **หลัง** split 80/10/10 แล้ว ขนาดสุดท้ายจึงไม่จำเป็นต้องมีอัตราส่วน 80/10/10
- label จริง:ปลอมใน manifest เป็น 1:2 แต่ training sampler เสนอให้สุ่ม label 1:1 แล้วสุ่ม G1/G2 เท่ากันเมื่อเลือก spoof ไม่ใช้ class weights เดิมซ้ำเพื่อชดเชยอีกครั้ง
- เสนอ cap ไม่เกิน 50 คลิปจริงต่อผู้พูดต่อ split ใน core cohort เพื่อไม่ให้คนเดียวครองข้อมูล หากทำให้จำนวนไม่พอให้ลดเป้าหมายหรือแก้ cap พร้อมเหตุผลก่อนล็อก ไม่ทำสำเนาคลิปเพื่อเติมจำนวน
- ถ้ามี G3 held-out เพิ่ม Test spoof 1,000 คลิปแยก manifest ไม่เปลี่ยน seen-generator Test ที่ล็อกแล้ว
- ต้องรายงานจำนวนผู้พูดจริง, ข้อความ, base clips, ชั่วโมง และ condition copies แยกกัน ห้ามนับเสียงที่เติม noise เป็นผู้พูด/ตัวอย่างอิสระใหม่
- ใช้ pilot วัดเวลาสร้างเสียงและพื้นที่ก่อนยืนยันจำนวนนี้ หากไม่พอให้แก้ config และบันทึก ไม่ลดข้อมูลเงียบ ๆ

<a id="s06"></a>
## 6. โครงสร้างไฟล์และการแบ่งงาน

เตรียมโฟลเดอร์หลัก/README และ package scaffold ตามโครงสร้างนี้แล้ว และมี Common Voice EDA notebook แบบง่าย ส่วน modules, executable YAML, TTS corpus และ training pipeline ด้านล่างยังเป็น **เป้าหมายที่ต้องพัฒนา** ดูรายละเอียดสถานะใน [PROJECT_STRUCTURE_TH.md](PROJECT_STRUCTURE_TH.md)

```text
configs/cvtts/
  protocol_v1.yaml                 # split/audio/conditions/training/metrics policy
  tts_registry.yaml               # model IDs, revisions, voices, licenses, envs
  runs/                           # resolved model × arm × seed configs
docs/
  COMMON_VOICE_PROJECT_WORKFLOW_TH.md
  PROJECT_STRUCTURE_TH.md          # สถานะและโครงสร้างที่มีจริง
  decisions/CVTTS_DECISIONS.md
  reports/cvtts/                   # sanitized summaries; ไม่ใส่ข้อมูลส่วนบุคคล
examples/inference_manifest.csv    # ชื่อไฟล์สมมติสำหรับ CLI เดิม ไม่ใช่ข้อมูลจริง
src/thai_spoof/cvtts/
  audit.py, split.py, schemas.py, provenance.py
  synthesis/                      # adapter ของ TTS แต่ละระบบ
  audio.py, conditions.py, datasets.py
  training/                       # common trainer + model-specific adapters
  scoring.py, evaluation.py, reporting.py
scripts/
  cvtts_pipeline.py               # command dispatcher ไม่อัดทุกอย่างในไฟล์เดียว
tests/cvtts/                      # ใช้ synthetic fixtures ที่แจกได้
data/raw/common_voice/<release>/  # ข้อมูลต้นทางแบบอ่านอย่างเดียว
data/raw/noise/<source>/          # แยก recording IDs / license
data/processed/cvtts/<version>/
  native_tts/                     # เสียง generator ที่ native sample rate
  canonical/                     # เสียงเต็ม mono 16 kHz
  conditions/                    # cache Dev/Test แบบ deterministic
  manifests/                     # CSV/Parquet และ source lineage; ไม่ commit
  qc/, jobs/, locks/              # ตรวจคุณภาพ, resume ledger, hashes
experiments/pilot/                 # งานทดลองเบื้องต้นที่มี implementation แล้ว
  notebooks/                      # EDA/TTS/canonical pilot
    outputs/                      # ผลที่รันแล้ว ไม่ commit
  scripts/, docs/                 # smoke/overfit diagnostics และคู่มือ
experiments/research/              # งานจริงยังเป็นแผน; ยังไม่มี main trainer
checkpoints/<model>/cvtts/<run_id>/
results/research/<protocol>/<run_id>/ # เสนอสำหรับ main runs; ผล pilot อยู่ results/pilot/
  resolved_config.yaml, environment.json, train_log.jsonl
  dev_scores.csv, threshold.json, test_scores.csv, metrics.json
  artifacts.json                 # input/output hashes และที่มาทั้งหมด
```

### 6.1 ข้อตกลงทีม

- งานร่วม: Common Voice cohort, split, TTS outputs, condition specification, label/score convention และ metrics ต้องใช้ชุดเดียวกัน
- ฝั่งผู้ใช้: AASIST training adapter และการทดลอง AASIST
- ฝั่งเพื่อน: RawNet2 training adapter และการทดลอง RawNet2
- กำหนดผู้ดูแล shared data/metrics หนึ่งคนต่อช่วง เพื่อลดการแก้ contract ชนกัน อีกคน review
- ไม่สร้างข้อมูลสองชุดต่างกันให้แต่ละโมเดลแล้วอ้างว่าเปรียบเทียบกันโดยตรง
- ห้ามส่งข้อมูลเสียง/token ผ่าน Git โดยไม่ตรวจเงื่อนไขสิทธิ์ ผู้ร่วมงานควรเข้าถึงต้นทางด้วยสิทธิ์ของตนเอง หรือใช้วิธีแบ่งปันที่ได้รับอนุญาต

### 6.2 Branch และ commit

- ผู้ใช้ไม่ต้องการ prefix `codex/` ให้ใช้ชื่อเช่น `feat-cv-audit`, `feat-cv-split`, `feat-tts-pipeline`, `feat-aasist-training`, `feat-rawnet2-training`, `feat-evaluation-protocol`
- ก่อนเริ่มทุกครั้งตรวจ `git status --short --branch` และ diff เดิม ห้ามทับ/ลบงานของผู้ใช้
- งานอิสระเริ่มจาก `main` ที่มี dependency ที่ต้องใช้แล้ว; งานที่ขึ้นกับ branch ที่ยังไม่ merge ต้องระบุฐานและเหตุผล ไม่แยกจาก branch อื่นเพียงเพราะกำลังอยู่ที่นั่น
- งานแผนเดิมรวมเข้าฐาน main แล้ว; งาน cleanup/โครงสร้างนี้แยกจาก main เป็น `refactor-common-voice-layout` ผู้ใช้เป็นคน commit เอง
- AI ผู้รับช่วง **ห้าม commit/push/merge หรือลบข้อมูลเอง** หากไม่ได้รับคำสั่งเพิ่ม
- หนึ่ง branch ต่อ feature ที่ตรวจสอบได้ อย่าเปลี่ยน data contract ทั้งโครงการพร้อมเพิ่ม model training โดยไม่มีจุด review

<a id="s07"></a>
## 7. Phase 0: ตกลงโจทย์ ตรวจเครื่อง และล็อกสิ่งแวดล้อม

### ขั้นตอนย่อย

1. อ่าน `AGENTS.md` ถ้ามีในตอนเริ่มงาน อ่านเอกสารนี้และตรวจ working tree
2. บันทึก research questions, main/optional experiments และเรื่องค้างยืนยัน
3. รัน environment check แบบอ่านอย่างเดียว ดู Python, Torch, CUDA, GPU/VRAM และ checkpoint ที่มีจริง; ตรวจ RAM และพื้นที่ว่างแยกด้วยเครื่องมือระบบ เพราะ `scripts/check_environment.py` ยังไม่ได้รายงานสองรายการหลัง
4. เก็บ source commit ของ project, AASIST upstream, RawNet2 source และ SHA-256 ของ checkpoint
5. เก็บ package versions ของ environment ที่ใช้งานได้ ห้ามอัปเกรด `.venv` หลักพร้อมติดตั้ง TTS โดยไม่จำเป็น
6. แยก detector environment ออกจาก TTS ที่ dependency ขัดกัน เช่น `.venv-tts-mms`, `.venv-tts-wayu` และ environment สำหรับ legacy TTS หากต้องใช้
7. ตรวจ FFmpeg และ codec ที่ต้องใช้จริง ยังไม่ถือว่ามีเพราะติดตั้ง Python packages แล้ว
8. เพิ่ม ignore rules ให้ข้อมูลเสียง, manifest ระดับคลิป, checkpoints, jobs, tokens, `.env`, `.venv-tts-*` ไม่ขึ้น Git ตรวจด้วย `git check-ignore`
9. กำหนด paths ผ่าน config/environment ไม่ hardcode drive D: ลงทุก module
10. สร้าง config/schema tests ขั้นแรกด้วยข้อมูลจำลอง ไม่ใช้เสียงจริงที่ติดเงื่อนไขเผยแพร่เป็น test fixture

**เครื่องที่ตรวจพบตอนจัดทำ:** RTX 3050 Ti Laptop VRAM 4 GB, Python 3.12.4, Torch 2.11.0+cu128 และ CUDA ใช้ได้ใน `.venv` ปัจจุบัน เป็นข้อมูลสถานะเครื่อง ไม่ใช่การรับรองว่า TTS/การฝึกทุกแบบจะพอดีหรือเสร็จในเวลาที่กำหนด

**ส่งมอบ:** decision log, environment snapshot, checkpoint/source hashes, skeleton config, storage budget และรายการ dependency ที่ต้องติดตั้งแยก

**Gate 0:** ทีมอธิบายโจทย์เดียวกันได้ รู้ที่มาของ checkpoint และมีพื้นที่/สิทธิ์พอสำหรับ pilot

### งานทฤษฎีที่ต้องทำควบคู่ ไม่รอจนถึงเขียนเล่ม

1. อ่านบทนำ วิธีการ และ evaluation protocol ของ paper AASIST และ RawNet2 anti-spoofing ตามลิงก์ด้านล่าง เทียบกับ source revision ที่ใช้จริง
2. ทำตารางอ่าน paper: งานแก้ปัญหาอะไร → รับ input แบบไหน → ส่วนประกอบ → dataset/split → loss/metrics → ผลที่ผู้เขียนรายงาน → ข้อจำกัด → สิ่งที่เรายืม/เปลี่ยน
3. สำหรับ TTS ทุกระบบที่เลือก อ่าน model card เรื่อง text frontend, acoustic model/vocoder, voices, training data ที่เปิดเผย, seed/parameters, native sample rate และสิทธิ์ แยกสิ่งที่รู้จากสิ่งที่ต้นทางไม่เปิดเผย
4. อธิบายความต่างของ “architecture”, “pretrained checkpoint”, “inference”, “fine-tuning” และ “สร้างข้อมูลด้วย inference ของ TTS” ให้ได้ โดยไม่เรียกทั้งหมดว่า train
5. ศึกษา SNR, bandwidth/codec, FAR/FRR/EER, speaker/text leakage และการเลือก threshold จาก Dev พร้อมทำตัวอย่างคะแนนง่าย ๆ ก่อนใช้ผลจริง
6. เขียน literature matrix และ theory notes ใน `docs/reports/cvtts/` โดยอ้างแหล่งตรง และแยกผล paper เดิมออกจากผลภาษาไทยของเรา

| ตัวตรวจจับ | กลไกที่ควรอธิบายได้ | เหตุผลที่นำมาเปรียบเทียบ / ข้อจำกัดที่ต้องวัด |
| --- | --- | --- |
| AASIST | รับ waveform แล้วสร้าง representation ใช้ graph attention เชื่อมข้อมูลด้านเวลาและความถี่ | ออกแบบให้พิจารณา artifact ทั้งสองด้านร่วมกัน แต่ผลจาก benchmark เดิมไม่รับประกันความทน noise/telephone/TTS ภาษาไทยของเรา |
| RawNet2 รุ่น anti-spoofing | รับ waveform ผ่าน sinc-based filtering, residual blocks, feature-map scaling และ GRU ก่อนจำแนกจริง/ปลอม | เป็นแนวทาง raw-waveform ที่รวมข้อมูลตามลำดับเวลา เหมาะเป็นระบบเปรียบเทียบต่างโครงสร้าง แต่ยังต้องวัด generalization และทรัพยากรจริง |

ที่มาของกลไก: [AASIST paper](https://arxiv.org/abs/2110.01200), [RawNet2 anti-spoofing paper](https://arxiv.org/abs/2011.01108) และ implementation ที่ตรวจใน repository อย่าสับสน RawNet2 รุ่นตรวจ spoof กับการใช้ RawNet2 ทำ speaker verification และอย่าสรุปว่าโมเดลใดเร็วกว่า/กิน RAM น้อยกว่าเพียงดูชื่อ architecture

ผลเปรียบเทียบทรัพยากรที่ต้องวัดใน pilot: trainable/total parameters, peak VRAM ขณะฝึก/ทำนาย, batch/input length, เวลา train ต่อ optimizer update และ inference latency/RTF บนเครื่องเดียวกัน กำหนด warm-up และใช้ GPU synchronization เมื่อจับเวลา ไม่ใช้ขนาดไฟล์ checkpoint แทน RAM ที่ต้องใช้ทั้งหมด

<a id="s08"></a>
## 8. Phase 1: สำรวจและคัด Common Voice

### 8.1 ตรวจที่มาและ metadata

1. เครื่องนี้มี Common Voice Thai 27.0 ที่ `data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/` แล้ว และมี basic EDA notebook; เมื่อทำต่อหรือย้ายเครื่องให้ตรวจ release/root จริงอีกครั้ง ไม่ hardcode จำนวนข้อมูลจากผลเก่า
2. บันทึก release, locale, download source/date, terms/license version, archive/file checksum ถ้ามี
3. อ่าน header ของ `validated.tsv` และไฟล์ประกอบจริง ใช้ชื่อคอลัมน์ตาม release ไม่บังคับ schema จากความจำ
4. ตรวจจำนวนแถว, ชนิดข้อมูล, missing/blank/unspecified, จำนวนค่าที่ไม่ซ้ำ และตัวอย่างค่าที่ไม่เปิดเผยตัวบุคคล
5. ตรวจ field ที่ใช้ได้ เช่น path, sentence, client_id และ demographic fields **เฉพาะเมื่อมีใน release นั้น**
6. ไม่รวม `validated.tsv` กับ `train.tsv/dev.tsv/test.tsv` ตรง ๆ เพราะอาจเป็นรายการที่ซ้อนกัน ใช้ validated เป็น candidate pool แล้วสร้าง split ของโครงงาน พร้อมเก็บ official split เป็น provenance ถ้าจับคู่ได้
7. ตัวเลข Common Voice 148,823 คลิปจากการสำรวจก่อนหน้าเป็นบริบทเก่า ต้องตรวจซ้ำกับ release/ไฟล์ที่จะใช้จริง ไม่ hardcode เป็นคำตอบใหม่

### 8.2 ตรวจเสียงและข้อความ

- ตรวจว่าทุก path อยู่ใต้ dataset root ไม่ยอมรับ path traversal
- ตรวจไฟล์มีจริง, decode ได้, sample rate/channels/duration และจำนวน samples ไม่เป็นศูนย์
- คำนวณ finite samples, peak, RMS, สัดส่วน samples ใกล้ full scale, สัดส่วน silence โดยกำหนดวิธีใน config
- สร้าง SHA-256 ของ file bytes และ fingerprint ของ decoded canonical PCM แยกกัน: byte hash จับไฟล์เหมือนกัน ส่วน PCM hash จับเสียง decode เหมือนกันภายใต้ pipeline เดียวกัน
- บันทึก sample rate/codec ต้นทาง ห้ามเขียนว่าเป็น WAV ต้นฉบับเพราะแปลง MP3 เป็น WAV แล้ว
- ตรวจข้อความว่าง, ความยาว, ตัวอักษรที่ไม่รองรับ, ตัวเลข, ชื่อเฉพาะ, ภาษาอื่นปน และเครื่องหมาย
- VAD/ASR ใช้เป็นตัวช่วย flag ได้ ไม่ใช้แทนการฟังตรวจหรือถือ transcript ของ ASR เป็นความจริงเด็ดขาด

### 8.3 เกณฑ์คัด v1 ที่เสนอ

1. ใช้ locale ภาษาไทยของ release ที่ยืนยัน; `validated` หมายถึงสถานะจากต้นทาง ไม่ใช่รับประกันคุณภาพทุกคลิป
2. ตัดออกแน่นอน: file missing/decode fail, zero length, NaN/Inf, all-zero waveform, text ว่าง, speaker key ว่างสำหรับ strict core cohort
3. คัด exact duplicate ให้เหลือหนึ่งรายการตามกฎ deterministic พร้อมเก็บ mapping ของ **source row IDs และ speaker keys ของสมาชิกทุกแถวก่อนลดข้อมูล** พร้อมเหตุผล เพื่อให้ขั้น split ยังเห็นความเชื่อมโยงทั้งหมด ไม่เหลือเพียง representative จนผู้พูดที่เชื่อมผ่านคลิปซ้ำหลุดไปคนละ split
4. เสนอช่วง duration 1–15 วินาทีสำหรับ pilot core cohort; สรุปว่าจะตัดไปเท่าใด แล้วตกลงช่วงจริงก่อนล็อก ไม่อ้างว่าโมเดลรับไฟล์ยาวกว่านั้นไม่ได้
5. flag เสียงเบา/เงียบมาก, clipping, speech mismatch สำหรับ review; threshold เชิงตัวเลขต้องกำหนดจาก Train pilot และล็อก ไม่เลือกด้วยคะแนน detector
6. การเก็บเฉพาะคลิปบางช่วงความยาว/ข้อความ/ผู้พูดทำให้ขอบเขตแคบลง ต้องแสดง retention table ก่อน–หลังและเหตุผลทุกขั้น
7. ไม่คัดข้อมูลออกเพียงเพราะ pretrained model ทายผิด เพราะจะทำให้ test ง่ายโดยออกแบบ

### 8.4 EDA ที่ต้องได้

- จำนวนคลิป/ผู้พูด candidate key/ข้อความไม่ซ้ำ/ชั่วโมง และ histogram ความยาวเสียง
- จำนวนและสัดส่วน missing ทุกคอลัมน์; แยก blank ออกจากค่าที่ระบุว่าไม่ทราบ
- การกระจายคลิปต่อผู้พูดและข้อความซ้ำระหว่างผู้พูด
- distributions ของ sample rate, channels, duration, RMS, peak และ quality flags
- อายุ/เพศ/สำเนียงถ้ามี: จำนวนคลิปและจำนวนผู้พูดแยกกัน ไม่เดาค่าที่หายจากเสียงหรือชื่อ
- รายการ duplicate groups, missing files และ exclusion reasons
- สรุปใน notebook ที่รันใหม่ได้ โดย outputs ระดับรายคนไม่เผยแพร่ใน Git

**ส่งมอบ:** source manifest, audit report, QC table, eligible candidate manifest และ notebook EDA

**Gate 1:** รู้ว่าข้อมูลคือ release ใด มีเท่าไร ใช้ได้เท่าไร และทุก exclusion ตรวจย้อนหลังได้

<a id="s09"></a>
## 9. Phase 2: แบ่งข้อมูลและป้องกันข้อมูลรั่ว

### 9.1 กติกาที่ห้ามละเมิด

Train/Dev/Final Test ต้องไม่แชร์:

1. speaker key ของเสียงมนุษย์ที่เชื่อถือได้ภายใน release
2. normalized text key ตามนิยามที่ล็อกไว้
3. exact duplicate audio group
4. ลูกหลานของ source clip เช่น TTS ที่ใช้ข้อความนั้น, crop, noise version และ telephone version

การ split ด้วย tuple `(speaker, text)` อย่างเดียว **ไม่พอ** เพราะคนเดียวกันอาจพูดหลายข้อความและกระจายไปหลายชุดได้

`client_id` เป็น dataset speaker key ที่ใช้จัดกลุ่ม ไม่ใช่หลักฐานยืนยันบุคคลจริงหนึ่งคนเสมอไป และไม่ควรพยายามระบุตัวบุคคลจากข้อมูลนี้

### 9.2 นิยาม normalized text ที่เสนอ

- เก็บข้อความเดิมเสมอ
- ใช้ Unicode NFC, trim และยุบ whitespace ซ้ำ; กำหนดการจัดการ zero-width characters ไว้ชัด
- สร้าง matching key เพิ่มที่ละความต่างของ punctuation/space บางชนิดเพื่อ flag ประโยคซ้ำใกล้เคียง โดยไม่แก้ข้อความต้นฉบับที่จะนำไปอ่านโดยไม่บันทึก
- ถ้าจะอ่านเลข/ตัวย่อใหม่ ให้เก็บ `tts_text` และ text normalization version แยกจากข้อความ Common Voice
- ให้การจัดกลุ่ม split ใช้ key ที่ครอบคลุมข้อความหลัง normalization ของ TTS ด้วย เพื่อไม่ให้คนละรูปเขียนกลายเป็นข้อความเดียวกันข้ามชุด
- ไม่ลบอักขระภาษาไทยแบบกว้าง ๆ จนคนละประโยคถูกจับเป็นประโยคเดียวโดยไม่ตรวจ

### 9.3 อัลกอริทึมที่นำไป implement ได้

1. เริ่มจาก eligible candidate manifest ของ Phase 1
2. สร้างกราฟเชื่อมรายการที่ share speaker / text key / duplicate group แล้วตรวจขนาด connected components โดยอ่าน duplicate membership/aliases ที่เก็บก่อนลดแถวจาก Phase 1 ด้วย
3. ถ้า components กระจายพอ ให้จัดทั้ง component ไป split เดียวแบบ seeded greedy allocation ใกล้ 80/10/10 พร้อมรายงานความคลาดเคลื่อนและความสมดุล
4. ถ้ามี giant component จนแยกไม่ได้ ให้ใช้ fallback ที่ประกาศไว้:
   - รวม speaker keys ที่ถูกเชื่อมด้วย duplicate audio เป็น speaker supergroups ก่อน
   - เรียง supergroups แบบ deterministic ด้วย hash ของ split seed และ group ID แล้วจัดเข้า split โดยคำนึงถึงจำนวนคลิปเป้าหมาย
   - สำหรับ text key ที่ปรากฏหลาย split เลือก owner เพียง split เดียวด้วย hash ของ `split_seed + text_key` เลือกจากรายชื่อ split ที่มีข้อความนั้นจริงและเรียงชื่อคงที่
   - เก็บข้อความนั้นเฉพาะ owner split; แถวใน split อื่นย้ายไป `excluded_cross_split_text` ไม่ย้ายตัวอย่างแบบสุ่มไปมาจน speaker รั่ว
   - ตรวจ duplicate group อีกครั้งและ purge/quarantine กลุ่มที่ยังข้าม split ตามกฎเดียวที่บันทึกไว้
5. เลือกวิธีหลักหรือ fallback จาก **ความเป็นไปได้ของข้อมูลก่อนดู model scores** เก็บ algorithm version และ retention ของทั้งวิธีที่พิจารณา
6. ภายในแต่ละ split เลือกหนึ่งคลิปจริงต่อข้อความด้วย seeded hash ordering แล้วคัดตาม speaker cap และจำนวนเป้าหมาย
7. ตรวจ intersections ของ speaker/text/duplicate/source lineage ว่างทั้งหมด หากไม่ว่างให้หยุด ไม่เตือนแล้วฝึกต่อ
8. บันทึก `split_assignment.parquet`, exclusion table, split report และ SHA-256 ของ manifests แบบเรียงแถว canonical
9. ตั้ง split ของ TTS เป็น split ของข้อความต้นทางทันที ห้ามสุ่ม split เสียงปลอมใหม่หลังสร้าง

การรักษา speaker/text isolation อาจทำให้ทิ้งข้อมูลจำนวนมาก ให้ลด cohort หรือปรับการออกแบบก่อนเริ่มทดลอง ไม่ผ่อนกติกาเงียบ ๆ เพื่อให้ครบจำนวน

### 9.4 Noise และ TTS ก็มี split

- แบ่ง noise ด้วย **รหัส recording ต้นทางก่อนตัด segment** ไม่ให้คนละช่วงจาก recording เดียวอยู่ Train และ Test
- เสนอแบ่ง noise recording 80/10/10 ด้วย seed คงที่ หาก pool เล็กเกินไปให้เพิ่ม recording หรือเปิดเผยข้อจำกัดก่อนเลือกใช้
- G1/G2 เป็น seen generators ใช้สร้าง Train/Dev/Test แต่ข้อความและ source lineage ต้องแยก
- G3 ถ้ามี ไม่ใช้เสียงของมันฝึก detector/เลือก hyperparameters/เลือก checkpoint จัดเป็น project-held-out generator
- คำว่า unseen ในรายงานต้องจำกัดว่า “ไม่ใช้ในขั้นพัฒนาตัวตรวจจับของโครงงาน” ไม่รับรองว่า pretrained detector/TTS ไม่เคยเห็นข้อมูลเกี่ยวข้องมาก่อน

**Gate 2:** split validator ผ่าน, มีจำนวนผู้พูด/ข้อความเพียงพอ, เก็บ hash แล้ว และยังไม่ได้ดู Final Test model scores

<a id="s10"></a>
## 10. Phase 3: ทดลองและเลือก TTS

### 10.1 รายการตั้งต้นสำหรับ feasibility pilot

รายการนี้เป็น candidate จากเอกสารต้นทาง ไม่ใช่คำรับรองว่ารันบนเครื่องนี้แล้ว เลือกหลังตรวจ revision/สิทธิ์/คุณภาพจริงเท่านั้น

| Candidate | บทบาทที่เสนอ | เหตุผลและข้อจำกัดสำคัญ |
| --- | --- | --- |
| `facebook/mms-tts-tha` | G1 | Thai VITS, text-only; weights CC-BY-NC 4.0 ต้องตรวจเงื่อนไข non-commercial และ pin revision |
| `wayu-ai/wayu-paxa-tts-edge` | G2 | Thai/English, เสียงสำเร็จรูปหลายเสียง, model card ระบุ 24 kHz/CPU และ weights CC-BY-NC 4.0; ต้องตรวจ dependency/คุณภาพ/acceptable-use terms และ license ของ code แยก |
| `lunarlist/tts-thai-last-step` | G3 ถ้าผ่าน pilot | Thai Tacotron2 + vocoder ตามตัวอย่าง; legacy dependencies และ license ของ vocoder ต้องตรวจแยก; ต้นทางระบุใช้ Common Voice จึงต้องรายงานความเสี่ยง pretraining overlap |
| `wannaphong/khanomtan-tts-v1.1` | สำรอง | รองรับไทยตามต้นทาง ต้องตรวจ stock voice/คุณภาพ; มีสายตระกูล VITS/YourTTS จึงไม่ถือว่าแตกต่างทางสถาปัตยกรรมมากเท่ากันทุกคู่ |

- ต้องใช้ model ID + commit/revision ที่เจาะจง ห้ามปล่อย `main/latest` ไหลเปลี่ยนระหว่างสร้าง dataset
- หลาย voice ของ TTS เดียวกันยังเป็น **หนึ่ง generator** ไม่ใช่หลายโมเดล
- การเปลี่ยน pitch/speed หรือ stochastic parameter ช่วยเพิ่มความหลากหลายบางด้าน แต่ไม่รับประกันลด overfitting และไม่แทนการทดสอบข้าม generator
- คำว่า noise ในพารามิเตอร์ภายใน VITS เป็นความสุ่มของตัวสร้างเสียง ไม่ใช่การเติม environmental noise ที่ SNR ของการทดลองนี้
- ไม่ใช้ reference-audio cloning model เป็น default หากต้องการใช้ต้องเพิ่ม consent/rights/conditioning split และอธิบายขอบเขตใหม่

อ้างอิง candidate โดยตรง: [MMS Thai](https://huggingface.co/facebook/mms-tts-tha), [Wayu model card](https://huggingface.co/wayu-ai/wayu-paxa-tts-edge), [Lunarlist model card](https://huggingface.co/lunarlist/tts-thai-last-step), [Khanomtan model card](https://huggingface.co/wannaphong/khanomtan-tts-v1.1) ให้ทำ pretraining-overlap audit เท่าที่ข้อมูลต้นทางเปิดเผย โดยเฉพาะ Lunarlist; ถ้าระบุสมาชิก Train ของ TTS ไม่ได้ ให้เขียนว่า unknown ไม่อ้าง speaker/text-unseen ต่อ TTS เอง แม้เราจะแยกข้อมูลของ detector ถูกต้องแล้ว

### 10.2 Pilot 50–100 ข้อความจาก Train

1. เลือกข้อความด้วย seed ครอบคลุมสั้น/ยาว ตัวเลข คำอังกฤษปน วรรคตอน และคำที่อาจอ่านยาก
2. ทดลองแต่ละ generator ใน environment แยก ใช้ default ที่ต้นทางแนะนำก่อน
3. เก็บ command/config, package versions, model revision, native sample rate, voice ID, seed, เวลา, memory peak และ failure
4. ฟังตรวจข้อความอย่างน้อย 30 ข้อความต่อ candidate แบบสุ่ม พร้อมรายการ edge cases แยก
5. ให้คนตรวจบันทึก intelligible / missing words / gibberish / repetition / silence / truncation / wrong language ไม่ใช้ “เหมือนคนมาก” เป็นเงื่อนไขเดียว
6. ตรวจ decode, duration, silence, clipping, text coverage และความสำเร็จของการ resume
7. วัด real-time factor: เวลา generate วินาที / ความยาวเสียงที่สร้างวินาที รายงาน CPU/GPU และ warm-up policy
8. ประมาณเวลาสร้าง corpus และพื้นที่จากผลจริง ไม่ใช้ตัวเลข speed ของ model card เป็นเวลาของเครื่องเรา
9. เลือกสองระบบที่ทำงานได้และมีความหลากหลายพอ โดยไม่ใช้ Final Test detector scores เลือก generator
10. ล็อก voice policy: ถ้ามีหลาย preset ให้สุ่มสมดุลด้วย hash ของ text ID/seed และเก็บ voice ทุกคลิป ใช้ policy เดียวข้าม split

**การใช้ G3 pilot:** ตรวจเพียงว่าอ่านภาษาไทย/สร้างไฟล์ได้โดยใช้ Train pilot text; ไม่ส่งเสียง G3 เข้า detector เพื่อเลือกวิธี ถ้าทำแล้วต้องเปลี่ยนสถานะเป็น development-seen หรือหา G3 ใหม่ที่ยังไม่ใช้เลือก detector

**Gate 3:** G1/G2 ใช้ได้จริงและตรวจสิทธิ์แล้ว ไม่มี blocker ด้าน dependency, มี quality report และ cost estimate จากเครื่องจริง หากมีแค่ระบบเดียวให้รายงานเป็น feasibility เท่านั้น ยังไม่อ้าง multi-generator experiment สมบูรณ์

<a id="s11"></a>
## 11. Phase 4: สร้างเสียงสังเคราะห์และตรวจคุณภาพ

### ขั้นตอนย่อย

1. สร้าง job table จาก frozen text/split manifest × selected generators × voice policy
2. สร้าง `generation_id` ด้วย stable hash ของ text key, generator ID/revision, voice, seed และ generation parameters
3. เก็บสถานะ `pending/running/done/failed`, attempts, error และ output hash เพื่อ resume ได้
4. เริ่มสร้างทีละ generator ไม่โหลด TTS หลายตัวและ detector training ลง GPU 4 GB พร้อมกัน
5. เขียนไฟล์ชั่วคราวแล้วตรวจ decode/hash ก่อน atomic rename ไปชื่อสุดท้าย ไม่ overwrite เสียงเดิมที่ generation ID/config ไม่ตรง
6. เก็บ native output ตาม sample rate จริงก่อน canonicalization; อย่าปรับ pitch/sample rate เพื่อให้ตัวเลขตรงโดยผิดวิธี
7. retry transient failure ได้ไม่เกิน 2 ครั้งหลัง attempt แรกด้วย config/seed เดิม ถ้ายังเสียให้ flag ไม่เปลี่ยน model/version เงียบ ๆ
8. ใช้ QC rule ที่ล็อกจาก Train pilot กับทุก split; ตรวจข้อความ/ไฟล์ได้ แต่ห้ามใช้คะแนน detector เลือกว่าคลิป Test ใดควรเก็บ
9. สำหรับ core paired cohort ถ้า real/G1/G2 ของข้อความหนึ่งไม่ผ่านหลัง retry ให้ตัดทั้ง bundle ด้วยเหตุผลที่บันทึก เพื่อให้ทุก run ใช้รายการเดียวกัน รายงานว่าการคัดแบบ complete bundle ทำให้ขอบเขตแคบลงเท่าใด
10. ตรวจ retention แยก split/generator/duration/voice ไม่ซ่อนว่าระบบหนึ่งสร้างข้อความยากไม่สำเร็จมากกว่าอีกระบบ
11. G3 เป็นชุดเสริม ถ้าไม่ผ่าน QC ใช้ subset พร้อม real คู่ข้อความที่ตรงกันและรายงานจำนวน ห้ามเอาผล subset นี้ไปเทียบตรงกับ seen cohort เต็มโดยไม่ทำ matched-subset comparison เพิ่ม
12. ตรวจ duplicate waveform/output collisions, wrong split และ source lineage อีกครั้ง
13. freeze `base_manifest` พร้อม hashes หลัง QC ห้ามแก้ไฟล์เดิม in-place เมื่อต้องเปลี่ยนข้อมูล ให้เพิ่ม dataset version

### สิ่งที่ต้องเก็บต่อคลิป TTS

- ข้อความที่ใช้จริง, generator/checkpoint revision, voice, parameters, seed
- source text/real clip ID สำหรับ lineage — ไม่ใช่การกล่าวว่า TTS เป็นเสียงของผู้พูดต้นทาง
- native/canonical sample rate, duration, file hash, QC และ license reference
- split ที่รับสืบทอดมา, generation timestamp, environment ID และ retry history

**Gate 4:** ทุกคลิปที่ใช้มีที่มาตรวจกลับได้, generation ledger สอดคล้องกับไฟล์, base cohort ล็อกแล้ว และยังไม่มี Test score ใช้คัดตัวอย่าง

<a id="s12"></a>
## 12. Phase 5: เตรียมเสียงและจำลอง condition

### 12.1 Shared audio pipeline

กำหนดลำดับเดียวกันสำหรับทั้งสองโมเดล:

1. Decode เป็น float32 → ตรวจ finite / nonempty
2. stereo/multichannel → mono ด้วย channel mean ตามกฎเดียวกัน บันทึก channels ต้นทาง
3. resample เป็น 16 kHz ด้วย implementation/version เดียว เช่น `scipy.signal.resample_poly` และพารามิเตอร์ที่ pin ไว้
4. ใช้ amplitude policy เดียว: ไม่ normalize แยกตาม label; ถ้า peak เกินช่วงที่อนุญาตให้ลด gain ตามกฎกลางและบันทึก ห้าม clip ทิ้งเงียบ ๆ
5. เก็บเสียงเต็ม canonical สำหรับ QC และ lineage
6. สร้าง input window 64,600 samples ตาม crop/pad policy
7. จึงใช้ Clean / Noise / Telephone transformation บน window นั้น
8. ตรวจความยาว, sample rate, finite และ range ก่อนส่ง tensor เข้า network

สำหรับ Train สุ่ม start จากจำนวนเต็ม `0..(length - 64600)` แบบรวมจุดท้าย ถ้าเท่ากัน start=0 ไม่เรียก random range ที่ว่าง ถ้าสั้นให้ repeat แล้วตัดครบ ไม่ใช้ zero padding โดยไม่เปลี่ยน protocol

Dev/Test ใช้ช่วงแรกเหมือนกันทั้งสองโมเดล การใช้ทั้งคลิปด้วย sliding windows เป็น **งานเสริมคนละ inference protocol** ไม่เปิด `--all-chunks` ให้ RawNet2 ฝ่ายเดียวแล้วเทียบกับ AASIST ที่ใช้ช่วงแรก

### 12.2 ความหมายของ Clean

Clean ในโครงงานนี้แปลว่า **ไม่เติม noise/telephone จำลองเพิ่ม** ไม่ได้แปลว่าเสียงต้นทางอัดในห้องไร้เสียงรบกวน Common Voice อาจมี background noise/codec อยู่แล้ว ต้องรายงานข้อจำกัดนี้

### 12.3 Noise

- เริ่มพิจารณา MUSAN non-speech noise หรือแหล่งที่มีสิทธิ์ใช้ชัดเจน ไม่เลือก music/speech ปะปนโดยไม่เพิ่มขอบเขต
- ล็อกรายการ noise recordings และการแบ่ง Train/Dev/Test ก่อนตัดช่วงเสียง
- crop/repeat noise ให้ยาวเท่า input; เก็บ recording ID, segment offset, seed และ gain
- นิยาม SNR ของ v1 ใช้กำลังเฉลี่ยของ **window ทั้ง 64,600 samples รวม silence** ไม่ใช่ active-speech SNR ถ้าจะเปลี่ยนต้องตั้ง version ใหม่

```text
Px = mean(x²)
Pn = mean(n²)
alpha = sqrt(Px / (Pn × 10^(SNR_dB/10)))
y = x + alpha × n
```

- ถ้า `Pn` ใกล้ศูนย์หรือไม่ finite ให้เลือก noise segment ใหม่ด้วย deterministic retry rule ที่ล็อกจำนวนครั้งไว้ พร้อม log; หากหมดตัวเลือกให้หยุด ไม่ข้ามแถวนั้นเงียบ ๆ
- ถ้า `Px` ใกล้ศูนย์หรือไม่ finite ให้จัดการที่ **base input ก่อนเลือก condition** ไม่เปลี่ยน/ทิ้งคลิปเฉพาะ Noise: Dev/Test ต้องตรวจ window แรกก่อนล็อก condition manifests หากไม่ผ่านให้ใช้ QC rule เดียวตัด bundle ทุก condition และออก dataset version ใหม่ก่อนฝึก; Train อนุญาต retry crop ไม่เกิน 3 ตำแหน่งตาม RNG กลางที่ Clean/Mixed ใช้ร่วมกัน แล้วหยุดเพื่อแก้ QC หากยังไม่มี window ที่ผ่าน
- ระบุ epsilon/energy floor ใน config และล็อกจาก Train pilot เสียงเต็มคลิปไม่เป็นศูนย์ไม่ได้รับประกันว่า window แรก 4.04 วินาทีจะมีเสียง
- ถ้า peak ของ mixture เกิน headroom ให้ลด gain ของ mixture และส่วนประกอบทั้งคู่ด้วยค่าเดียวกัน จึงคง SNR ไม่ hard-clip ซึ่งสร้าง artifact เพิ่ม
- ตรวจ SNR ที่ได้ก่อน/หลัง gain ด้วย synthetic test ยอมคลาดเคลื่อนตาม tolerance เช่น 0.2 dB และระบุว่า tolerance นี้ใช้กับ mixture noise ขั้นนี้ ไม่ใช่หลังผ่าน telephone
- Train เลือก noise segment/SNR ตาม RNG คงที่ต่อ sample occurrence; Dev/Test ใช้ condition manifest คงที่ ไม่สุ่มใหม่เมื่อ score อีกโมเดล
- สำหรับ `base_clip_id` เดียวกันใน Test ให้ Noise 20/10/0 dB ใช้ **recording, offset และ noise waveform เดียวกัน เปลี่ยนเฉพาะ gain** เพื่อแยกผลของ SNR; cache/manifest เดียวกันใช้กับทุก model/arm/seed
- ไม่เติม noise เฉพาะ spoof เพราะ detector อาจเรียนว่ามี noise = spoof

### 12.4 Telephone profile v1 — แบบจำลองที่ต้อง implement และทดสอบ

ข้อเสนอ narrowband simulation:

1. รับ window mono 16 kHz
2. band-pass 300–3,400 Hz เช่น Butterworth `N=6` แบบ SOS; บันทึกว่า N คือค่าที่ส่งให้ filter design และเก็บ coefficients/phase method จริง
3. anti-aliased resample 16 kHz → 8 kHz
4. G.711 μ-law encode/decode ที่ 8 kHz ผ่าน implementation ที่ตรวจแล้ว เช่น FFmpeg ที่มี `pcm_mulaw`
5. resample 8 kHz → 16 kHz
6. ตรวจได้ 64,600 samples และบันทึกการชดเชยความยาว/latency ถ้ามี ห้ามเลื่อน waveform แบบสุ่มต่างกันระหว่าง label

ต้องตรวจว่า FFmpeg build รองรับ codec จริงก่อนใช้ ไม่พึ่ง module เก่าที่อาจไม่มีใน Python รุ่นใหม่โดยไม่ล็อก environment

นี่คือ **ช่องสัญญาณโทรศัพท์ narrowband จำลอง** ไม่รวม VoLTE/VoIP/packet loss/ไมโครโฟน/ลำโพงหรือโทรศัพท์ทุกรุ่น หากอาจารย์ต้องการสถานการณ์จริงต้องออกแบบชุดเสริมต่างหาก

### 12.5 ความเป็นธรรมและ shortcut ที่ต้องระวัง

- Common Voice อาจมาจาก MP3 ส่วน TTS ออกมาเป็น waveform; การแปลงทั้งสองเป็น WAV ไม่ลบร่องรอย codec ที่ฝังมาแล้ว
- ใช้ preprocessing เดียวเป็นขั้นต่ำ แต่ไม่รับประกันว่าตัด codec/channel shortcut หมด
- ตรวจ duration, RMS, silence, sample rate และ codec distributions แยก label/generator และเก็บก่อน/หลัง transform
- ก่อน Final Test ควรกำหนด codec/channel sensitivity analysis เพิ่มที่แปลงทั้งสอง label ด้วย chain เดียวกันและใช้ threshold เดิม รายงานเป็นข้อจำกัด/robustness check ไม่อ้างว่าพิสูจน์ขจัด shortcut ได้หมด
- ทั้ง Clean/Mixed ต้องเลือก base samples ด้วย policy เดียว Mixed ไม่ได้ข้อมูลมากกว่าโดยปล่อยให้ epoch มี optimizer updates สามเท่า

**Gate 5:** condition tests ผ่าน, Dev/Test cache/manifest deterministic, ไม่มี noise recording ข้าม split และทั้งสองโมเดลได้รับ tensor ที่ตรงกันสำหรับ clip/condition เดียวกัน

<a id="s13"></a>
## 13. Phase 6: สร้างระบบฝึกและประเมินที่ใช้ร่วมกัน

### 13.1 Training adapters

กำหนด contract ของ adapter ให้ชัด:

- โหลด architecture/config/init checkpoint ที่ระบุ พร้อมตรวจ missing/unexpected keys อย่างเข้มงวด
- `forward_train(waveform)` คืน output ที่ gradient ไหลได้; ไม่ผ่าน inference-mode wrapper
- AASIST: ใช้ class logits จาก output ของ network กับ cross-entropy
- RawNet2: ตรวจว่ารุ่นที่ใช้คืน log-softmax; ถ้าใช่ใช้ NLL loss หรือเปิด logits อย่างมีแบบทดสอบ ห้ามนำ output มาตีความแบบสุ่ม
- ตรวจ output class order และ batch shape จากตัวอย่าง/fixture ห้ามเชื่อชื่อ index โดยไม่ตรวจ
- checkpoint inference loader ต้องรับ path ของน้ำหนักที่ fine-tune แล้วได้ มิฉะนั้นอาจฝึกสำเร็จแต่เผลอประเมิน pretrained เดิม
- รักษา CLI เดิมให้ใช้งานได้ หลีกเลี่ยงแก้ upstream source จำนวนมากโดยไม่จำเป็น ใช้ adapter ใน project ก่อน

### 13.2 Score convention

กำหนด score ใหม่ที่ใช้ร่วมกันใน pipeline นี้:

```text
bonafide_score = output_bonafide - output_spoof
```

- AASIST ใช้ผลต่าง logits; RawNet2 ใช้ผลต่าง log-probabilities ถ้า output เป็น log-softmax
- คะแนนมาก = มีแนวโน้มเป็นเสียงจริง คะแนนนี้ไม่ใช่ calibrated probability
- บันทึก `score_type` เช่น `bonafide_margin_v1` และ class mapping ในทุก run
- โมเดลต่างกันยังมี score scale ต่างกันได้ จึงเลือก threshold แยกต่อ run ไม่ใช้ตัวเลข threshold ร่วมข้าม AASIST/RawNet2
- ต้อง rescore pretrained references ด้วยนิยามเดียวกัน อย่าเอา CSV เก่าที่เป็น probability/คนละ output มาปน

### 13.3 EER และ fixed-threshold metrics เป็นคนละเรื่อง

นิยามการตัดสินสำหรับ threshold τ:

```text
score >= τ → bonafide
score <  τ → spoof

Real-as-fake rate (FRR) = จำนวน bonafide ที่ score < τ / bonafide ทั้งหมด
Fake-as-real rate (FAR) = จำนวน spoof ที่ score >= τ / spoof ทั้งหมด
```

- ใช้ `y=1` สำหรับ bonafide และ score มากเป็น bonafide จึงได้ FAR จาก ROC false-positive rate และ FRR = 1 − true-positive rate
- EER คือจุดที่ FAR กับ FRR เท่ากันหรือค่าประมาณที่นิยามไว้จาก ROC; ให้ implement **linear interpolation ที่จุดตัด FAR−FRR=0** พร้อมจัดการ ties อย่างสม่ำเสมอ และเขียนชื่อ method ในรายงาน
- EER เป็น metric ของ test scores ที่อนุญาตให้คำนวณโดยกวาด threshold แต่ threshold ที่ได้จาก Test EER **ห้ามนำไปเป็น operational threshold ของ Test predictions**
- ค่า accuracy/confusion/FAR/FRR สำหรับการใช้งานจริง ต้องใช้ threshold ที่เลือกจาก Dev เท่านั้น
- ปฏิเสธคะแนน NaN/Inf และ split ที่มีเพียง label เดียวสำหรับ EER; ไม่แทนด้วยศูนย์
- ให้เทียบกับ official ASVspoof evaluation implementation บนกรณีที่เหมาะสม และบันทึกความต่างของ tie/interpolation convention ไม่อ้างว่า implementation ทุกแบบให้เลขเท่ากันเสมอ

### 13.4 เลือก threshold จาก Dev

1. ใช้ best checkpoint ของ run นั้น score Dev ทั้ง Clean, Noise 10 dB และ Telephone
2. แต่ละ condition ต้องมีรายการ base clips เท่ากัน แล้ว pool Dev scores เพื่อให้แต่ละ condition มีน้ำหนักเท่ากัน
3. พิจารณา finite operating thresholds ที่ครอบคลุมจุดเปลี่ยนของ scores และปลายช่วงตาม convention `>=`
4. เลือก threshold ที่ทำให้ `abs(FAR−FRR)` ต่ำสุด; ถ้าเสมอเลือก FAR ต่ำกว่า แล้วเลือก threshold ตัวเลขสูงกว่าอย่าง deterministic
5. ห้ามเอา threshold `inf` เริ่มต้นของ ROC ไป interpolate จนได้ค่าที่ใช้จริงไม่ได้ ต้องมี tests สำหรับ constant/tied scores
6. บันทึก `threshold.json`: τ, score type, label mapping, Dev manifest hash, condition weights, checkpoint hash และ rule version
7. ใช้ τ เดิมกับ Test ทุก condition ของ run นี้ ไม่ calibrate ใหม่จาก Test หรือต่อ Test condition

**Gate 6:** gradient/loss/score/threshold tests ผ่าน และได้คะแนน/คำตอบเหมือนเดิมเมื่อ reload checkpoint เดิมใน tolerance ที่ประกาศ

<a id="s14"></a>
## 14. Phase 7: Fine-tune และเลือก checkpoint

### 14.1 เริ่มจาก smoke test และ overfit-small-batch test

1. ใช้ Train subset เล็กที่มีทั้งสอง label และสอง generators
2. forward/backward 1–5 updates; ตรวจว่า loss/gradients finite และ parameters เปลี่ยนจริง
3. ทดลองจำ subset เล็กเพื่อจับ label/loss/data bug ไม่ใช้ผลนี้อ้าง generalization
4. save/reload แล้ว score ชุดเดิม ผลต้องตรงตาม tolerance
5. interrupt/resume แล้วตรวจ step, optimizer, RNG, sampler และ log ไม่เริ่มทับ run เดิม
6. ประเมิน peak VRAM/time ด้วย batch จริงแล้วจึงเลือก batch สำหรับ main runs

### 14.2 ค่าเริ่มต้น pilot ที่เสนอ

| Parameter | ค่าเริ่มต้น | หมายเหตุ |
| --- | --- | --- |
| Optimizer | AdamW | ข้อเสนอของโครงงาน ไม่ใช่ recipe ทางการที่พิสูจน์ดีที่สุด |
| Learning rate | 1e-5 | ปรับจาก Train/Dev ได้ด้วยงบที่บันทึก |
| Weight decay | 1e-4 | ใช้เหมือนกันระหว่าง arms ของ model เดียวกัน |
| LR schedule | constant | ลดความซับซ้อนรอบแรก; ถ้าเปลี่ยนให้ล็อก config ใหม่ |
| Microbatch | 2 | ตรวจว่า VRAM พอจริง |
| Gradient accumulation | 8 | effective batch 16 เมื่อ microbatch=2 |
| Main pilot budget | 2,000 optimizer updates | ไม่ใช่ 2,000 microbatches; ประเมินความพอจาก Dev ก่อนล็อก |
| Dev frequency | ทุก 100 optimizer updates | และท้าย run |
| Gradient clip | norm 1.0 | log clipping/nonfinite events |
| Precision | float32 หรือ AMP ที่ตรวจแล้ว | บันทึกชนิด; gradient accumulation ไม่แก้ BatchNorm แบบ batch ใหญ่ |
| Checkpoint selection | mean EER ของ Dev 3 conditions ต่ำสุด | ถ้าเสมอเลือก checkpoint step ก่อนกว่า |

ถ้า batch 2 ไม่พอ ลด microbatch/เพิ่ม accumulation ได้ แต่ต้องบันทึกและพิจารณา BatchNorm โดยเฉพาะ batch 1 ห้ามสรุปว่า effective batch เท่ากันแปลว่าพฤติกรรมเหมือนกันทุกด้าน

### 14.3 Fair comparison

- ภายใน model เดียวกัน Clean/Mixed เริ่มจาก checkpoint hash เดียวกัน มี optimizer settings, update count, effective batch, seeds และ checkpoint criterion เดียวกัน
- ใช้ sampler ของ base clip / label / generator / crop ที่แยก RNG จาก augmentation เพื่อให้ Clean/Mixed เจอลำดับ base ตัวอย่างเดียวกันตาม seed
- Mixed เปลี่ยนเพียง condition waveform; ไม่เปลี่ยน label weighting, data budget หรือเลือก checkpoint ด้วย metric คนละแบบ
- สุ่ม label เท่ากัน; เมื่อ spoof สุ่ม generator เท่ากัน แล้วสุ่มคลิปจาก pool ที่ speaker cap แล้ว บันทึก exposure counts จริง
- ไม่ early-stop arm หนึ่งเร็วเพียงเพราะผลดูดี อีก arm ได้ updates มากกว่า โดยไม่มี protocol ที่เทียบได้
- ถ้าปรับ hyperparameters ต่างกันระหว่าง AASIST/RawNet2 ให้ใช้ tuning budget เท่าเทียมและบันทึกครบ พร้อมจำกัดข้อสรุปเรื่อง architecture
- ใช้ Dev เท่านั้นสำหรับการลอง LR/step budget อย่ารวม Test loader ไว้ใน training loop
- เริ่มจาก pilot seed เดียวของทั้งสี่แบบ; เมื่อล็อก training recipe แล้วเริ่ม main runs ใหม่ทุกแบบจาก init ไม่เอา pilot ที่เลือกจากผลดีมาแทน run หลัก

### 14.4 สิ่งที่ต้องบันทึกในทุก run

- run ID = protocol/model/arm/seed; resolved config และ environment/source/dataset hashes
- loss, LR, update step, samples seen, per-label/generator/condition exposure, gradient norm, elapsed time, peak VRAM
- Dev EER แยก condition และค่าเฉลี่ยที่ใช้เลือก checkpoint
- `best` และ `last` checkpoint พร้อม model, optimizer, scheduler ถ้ามี, AMP scaler, RNG states และ sampler state
- failures/resume history; ห้ามสร้างไฟล์ผลปลอมเมื่อ run ล้ม
- best step, total updates, wall time และเหตุผลการเลือก

**Gate 7:** main runs ตามงบที่ตกลงครบ, best checkpoints โหลดได้, ไม่มี Test feedback, thresholds ของทุก run ถูก freeze แล้ว

<a id="s15"></a>
## 15. Phase 8: Final Test และวิเคราะห์ผล

### 15.1 Checklist ก่อนเปิดคะแนน Test

- [ ] split/cohort/generator revisions/noise pools และ hashes ล็อกแล้ว
- [ ] training recipe, seeds, checkpoints และ Dev thresholds ล็อกแล้ว
- [ ] ระบุ primary/secondary metrics, EER method และ condition averaging rule แล้ว
- [ ] score direction/class order และ fixed-threshold code ผ่าน tests
- [ ] ไม่มีใครใช้ Test detector scores เพื่อคัดข้อมูล/เลือก generator/เลือกรุ่นมาก่อน
- [ ] มี `protocol.lock.json` หรือ artifact manifest เชื่อมไฟล์ข้างต้นครบ

การ QC Test ก่อนหน้านี้ทำได้เฉพาะเชิงข้อมูลตามกฎที่ล็อก เช่น decode fail/text mismatch ไม่ใช่ดูผลทำนายแล้วออกแบบให้ดีขึ้น

### 15.2 รัน scoring

1. score ทุก run บน seen-generator Test แยก Clean, Noise 20/10/0 dB และ Telephone
2. เก็บ raw score ต่อคลิป ไม่เก็บเฉพาะสรุป EER เพื่อให้ตรวจซ้ำและทำ paired analysis ได้
3. ตรวจครบทุก clip/condition ไม่มีแถวซ้ำ ไม่มี missing scores และ checkpoint hash ตรง run
4. คำนวณ EER ต่อ condition และ FAR/FRR/confusion จาก Dev threshold
5. ถ้ามี G3 ทำชุด held-out แยก พร้อม matched-subset comparison ถ้า QC ทำให้จำนวนต่าง
6. ประเมิน pretrained reference แบบเดียวกันได้ แต่ห้ามใช้ผลของมันบน Final Test มาย้อนเลือก training recipe
7. ถ้าพบ implementation bug หลังเปิดคะแนน ให้บันทึก bug/fix/rerun และผลกระทบครบ ไม่เลือกใช้เฉพาะ rerun ที่ตัวเลขดีขึ้น

### 15.3 ตารางผลขั้นต่ำ

| Model | Train arm | Seed | Test condition | Generator scope | N real / spoof | EER % | FAR % ที่ τ_dev | FRR % ที่ τ_dev |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AASIST | Clean | … | Clean / Noise / Telephone | G1+G2 / G3 | … | … | … | … |
| AASIST | Mixed | … | … | … | … | … | … | … |
| RawNet2 | Clean | … | … | … | … | … | … | … |
| RawNet2 | Mixed | … | … | … | … | … | … | … |

- รายงานทุก seed แล้วจึง mean/SD ข้าม seeds ไม่เลือกแต่ค่าต่ำสุด
- รายงาน EER แยก G1/G2 ได้โดยใช้ bona fide comparison set เดียวกัน แต่ pooled Test ต้องนับ real clip เพียงครั้งเดียว ไม่ทำสำเนา real ซ้ำตามจำนวน generators
- รายงาน `ΔEER = EER_Mixed − EER_Clean` เป็น percentage points; ค่าติดลบคือ Mixed ดีกว่าในเงื่อนไขนั้น
- ถ้าจะรายงาน relative reduction ต้องแยกจาก percentage points และจัดการกรณี Clean EER=0 ไม่หารศูนย์
- สรุป robustness ของ Noise 20/10/0 และ Telephone แยกกันก่อนค่าเฉลี่ย; ถ้าค่าเฉลี่ยใช้ให้กำหนดน้ำหนักเท่ากันล่วงหน้า อย่าใช้จำนวนแถวให้ condition ที่ทำสำเนามากกว่าครองผล
- เก็บ confusion matrix ต่อ run/condition และตารางความผิดพลาดตาม duration/generator/voice/quality flags เป็น exploratory analysis

### 15.4 ความไม่แน่นอนและความเป็นอิสระ

- หลายคลิปจากคนเดียวกันและหลาย condition จากคลิปเดียวกันไม่ใช่ตัวอย่างอิสระทั้งหมด
- แนะนำ paired cluster bootstrap 1,000–2,000 รอบ ถ้างบพอ โดยสุ่ม cluster ของ source speaker และพาทุกข้อความ/real/TTS/condition ใน cluster มาด้วย
- ใช้ cluster draws เดียวกันระหว่าง Clean/Mixed และระหว่างโมเดลที่เปรียบเทียบ เพื่อรักษาความเป็น paired data
- speaker key บน TTS ใช้เป็น **source lineage cluster เพื่อการสุ่มสถิติ** ไม่ใช่คำกล่าวว่า TTS เป็นคนคนนั้น
- แยก confidence interval จากการสุ่มข้อมูลออกจาก SD ของ training seeds ระบุวิธี aggregation ไม่ปนเป็นค่าชนิดเดียวกัน
- bootstrap replicate ที่ขาด label ต้องจัดการตามกฎ ไม่แอบใส่ EER=0

### 15.5 ถ้าทำ demographic analysis

- ใช้ข้อมูลจริงที่ผู้ให้ข้อมูลระบุ/ต้นทางมี แยก unknown/blank ไม่เดาอายุ เพศ หรือถิ่นจากเสียง
- รายงานจำนวนผู้พูดและคลิปต่อกลุ่ม พร้อมช่วงความไม่แน่นอนและข้อจำกัดกลุ่มขนาดเล็ก
- บนเสียงจริงอย่างเดียวรายงาน **real-as-fake rate** ที่ threshold เดิม ไม่คำนวณ EER เพราะไม่มีสอง label
- ข้อความของผู้พูดอายุ 20 ปีที่นำไปให้ TTS อ่าน ไม่ทำให้ TTS นั้นเป็นเสียงคนอายุ 20 ปี ห้าม copy demographic labels ไปอ้างเป็นคุณลักษณะเสียงปลอม
- จังหวัด/ที่อยู่/สำเนียงเป็นคนละตัวแปร และ preset voice เช่น “young” ไม่ใช่ demographic ground truth

**Gate 8:** ผลทุกรายการตรวจย้อนกลับได้, metrics ใช้ protocol ที่ล็อก, ข้อผิดพลาด/ข้อจำกัดเปิดเผย และไม่มีการวน Final Test เพื่อปรับ model

<a id="s16"></a>
## 16. Phase 9: รายงานและการส่งมอบ

### สิ่งที่ต้องใส่ในรายงาน

1. ปัญหาและขอบเขต: ตรวจเสียงสังเคราะห์ ไม่เท่ากับตรวจเจตนาฉ้อโกง
2. ทฤษฎี: waveform/sample rate, TTS เทียบกับ detector, AASIST/RawNet2, fine-tuning, overfitting/generalization, noise/SNR, telephone simulation, EER/FAR/FRR และ data leakage
3. Dataset: Common Voice release/terms, cohort flow, QC, split algorithm, จำนวนผู้พูด/ข้อความ/ชั่วโมง, generator/voice/revision และ lineage
4. Method: preprocessing, window/crop/repeat, conditions, sampling, training settings, checkpoints และ Dev-only selection
5. Experimental matrix: สี่ arms, seeds, seen/held-out generators, compute budget และ pretrained references ถ้ามี
6. Results: ตารางทุก condition/seed และความต่าง Clean/Mixed พร้อม uncertainty ที่คำนวณได้
7. Analysis: noise robustness, telephone degradation, generator generalization, clean trade-off และข้อผิดพลาด
8. Limitations: speaker IDs ไม่ยืนยันคนจริง, codec artifacts, TTS diversity, data selection bias, unknown pretraining overlap, simulated telephone และ hardware budget
9. Ethics/licensing: สิทธิ์เข้าถึง/ไม่เผยแพร่ข้อมูลเกินเงื่อนไข, ไม่ใช้ clone คนโดยพลการ, ไม่แสดงผลเป็นคำตัดสินเด็ดขาด
10. Reproducibility: source commit, configs, environment versions, manifest hashes, checkpoints และคำสั่งที่ใช้จริง

### เกณฑ์สำเร็จของโปรเจกต์

- ระบบทำงานครบจากข้อมูลที่ตรวจที่มาแล้วไปถึงผลประเมินที่ทำซ้ำได้
- มีการเปรียบเทียบสี่แบบอย่างยุติธรรมภายใต้ขอบเขตที่ตกลง
- ไม่รั่ว Train/Dev/Test และไม่เลือก threshold/recipe จาก Final Test
- ตอบได้ว่า Mixed ช่วยหรือไม่ ช่วยที่ condition ใด แลกกับอะไร และยังสรุปอะไรไม่ได้
- มีผลเชิงลบ/ความล้มเหลว/ข้อจำกัดรายงานตามจริง ไม่จำเป็นต้องทำให้โมเดลใด “ชนะ” ก่อนถือว่าจบ

<a id="s17"></a>
## 17. Data contracts: ฟิลด์ที่ต้องเก็บ

ฟิลด์ต่อไปนี้เป็นของ pipeline ที่ต้องสร้าง ไม่ใช่การอ้างว่ามีอยู่ใน Common Voice ต้นฉบับทั้งหมด ให้ใช้ schema validation และ version ทุก manifest

### 17.1 Source / split manifest — หนึ่งแถวต่อคลิปจริงต้นทาง

| Field | ความหมาย |
| --- | --- |
| `source_clip_id` | ID คงที่ที่สร้างจาก release + relative path/ต้นทาง |
| `dataset_id`, `dataset_release`, `locale` | ระบุแหล่งและรุ่น ไม่ใช้คำว่า latest |
| `source_relpath` | path ใต้ dataset root ไม่ใช่ path drive ของเครื่องใดเครื่องหนึ่ง |
| `speaker_key` | pseudonymous group key จากต้นทาง; ไม่ใช่ชื่อจริง |
| `text_original`, `tts_text` | ข้อความเดิมและข้อความที่จะสังเคราะห์ |
| `text_key`, `normalization_version` | กลุ่มข้อความสำหรับตรวจ leakage |
| `official_split`, `project_split` | provenance ต้นทางถ้ามี และ split ที่โครงงานสร้าง |
| `file_sha256`, `pcm_sha256`, `duplicate_group_id` | ตรวจซ้ำและย้อนที่มา |
| `source_sr`, `source_channels`, `duration_s` | คุณสมบัติที่อ่านจากเสียงจริง |
| `qc_status`, `exclusion_reason` | ผ่าน/รอตรวจ/ตัดออก และเหตุผล |
| demographic columns ถ้ามี | เก็บค่าต้นทางพร้อม missing policy ไม่เติมค่าที่เดา |

### 17.2 Base manifest — หนึ่งแถวต่อเสียงจริงหรือเสียง TTS เต็มคลิป

| Field | ความหมาย |
| --- | --- |
| `clip_id`, `base_clip_id` | ID เสียงหลัก; condition descendants จะอ้างถึง ID นี้ |
| `source_clip_id`, `text_key`, `source_speaker_key` | lineage เท่านั้น โดยเฉพาะสำหรับ TTS |
| `project_split`, `label`, `label_id` | split และคำตอบจริงจากที่มา ไม่ใช้ model prediction เป็น label |
| `generator_id`, `generator_revision`, `voice_id` | สำหรับ spoof; real ใช้ null พร้อมเหตุผลว่า not applicable |
| `generation_id`, `generation_seed`, `generation_params` | ทำซ้ำเสียงและแยก generation variants |
| `native_relpath`, `canonical_relpath` | ที่เก็บ native/canonical audio |
| `native_sr`, `canonical_sr`, `duration_s`, `n_samples` | ข้อมูลเสียงที่ตรวจแล้ว |
| `audio_sha256`, `qc_status`, `dataset_version` | integrity และรุ่นของ corpus |
| `license_ref`, `environment_id` | ที่มาสิทธิ์และ environment ที่ผลิต |

### 17.3 Condition manifest — หนึ่งแถวต่อ input ที่นำไปประเมิน

- `eval_item_id`, `base_clip_id`, `project_split`, `condition_id`, `condition_version`
- `crop_start`, `crop_length`, `padding_policy`, `audio_pipeline_version`
- `noise_recording_id`, `noise_offset`, `snr_db`, `noise_gain`, `mixture_gain` หรือ null เมื่อไม่ใช้
- `telephone_profile`, `transform_seed`, `cache_relpath`, `waveform_sha256`
- ใช้ unique key ของ `(base_clip_id, condition_id, protocol_version)` สำหรับ v1 ที่มี window เดียว

Train ไม่จำเป็นต้อง materialize ทุก augmentation แต่ต้อง reconstruct ได้จาก run seed, epoch/step, sample occurrence และ config โดยไม่เก็บเสียงซ้ำทั้งหมด

### 17.4 Scores / thresholds / metrics

- Scores: `run_id`, `checkpoint_sha256`, `eval_item_id`, `label`, `condition_id`, `generator_id`, `bonafide_score`, `score_type`
- Predictions: `threshold_id`, `threshold_value`, `predicted_label` ที่คำนวณจาก Dev threshold เท่านั้น
- Metrics: sample counts, label counts, EER method/value, FAR/FRR, confusion, seed, condition scope, input hashes
- Thresholds: rule/Dev conditions/weights/score direction/class order/checkpoint hash ตามส่วน 13
- ทุก merge/join ต้องตรวจ one-to-one หรือ many-to-one ตาม contract ไม่ปล่อย duplicate join เพิ่มจำนวนแถวเงียบ ๆ

### 17.5 หลักการ missing values

- แยก `unknown` (ควรมีแต่ไม่ทราบ), `not_applicable` (เช่น generator ของเสียงจริง), `missing_file` และ `not_measured`
- ไม่แทน missing age ด้วย 0 หรือ missing speaker ด้วย ID เดียวแล้วเข้าใจว่าเป็นคนเดียวกัน
- ห้ามใช้ path, label, generator ID หรือ demographic field เป็น input detector หลัก โมเดลรับ waveform เท่านั้น metadata ใช้จัดการ/วิเคราะห์

<a id="s18"></a>
## 18. Quality gates และรายการทดสอบ

| Gate | ต้องผ่านอะไร | ถ้าไม่ผ่าน |
| --- | --- | --- |
| 0 | scope/สิทธิ์/environment/pilot budget | หยุดดาวน์โหลดหรือสร้างเสียงจำนวนมาก |
| 1 | source audit/QC/retention | แก้ source paths/schema/เกณฑ์ ไม่เริ่ม split |
| 2 | speaker/text/duplicate/lineage isolation | หยุดทุก training จน split ถูกต้อง |
| 3 | TTS ≥2 ระบบผ่าน feasibility/สิทธิ์ | เปลี่ยน candidate ก่อนล็อก หรือขอลดขอบเขต |
| 4 | synthesis/QC/base manifest frozen | retry/review ตามกฎ ไม่คัดด้วย detector |
| 5 | shared input/conditions/noise isolation | แก้ audio pipeline และ regenerate cache ตาม version |
| 6 | training/score/threshold unit tests | ไม่ใช้ผล metrics ที่ยังผิดทำข้อสรุป |
| 7 | main runs/checkpoints/Dev thresholds ครบ | ยังไม่เปิด Final Test |
| 8 | Test integrity/reproducibility/report | ตรวจสาเหตุและเปิดเผย reruns |

### Unit tests ที่ต้องเขียน

- Text: NFC/space/zero-width normalization คงที่ ไม่ทำลายตัวอักษรไทย และ text collision ถูก flag
- Split: คนเดียวหลายข้อความ, ข้อความเดียวหลายคน, duplicate ข้าม speaker, giant component, missing speaker, deterministic rerun และ no intersection
- Audio: mono/stereo, sample rates ต่าง, empty/NaN/Inf/all-zero, length ต่ำกว่า/เท่ากับ/มากกว่า 64,600, random crop รวม start สุดท้าย และ repeat ถูกต้อง
- Noise: SNR ตรงสูตร, zero-energy guards, no clipping, seed deterministic, SNR variants ใช้ noise segment เดียวกัน, invalid input ไม่ทำให้ base lists ต่างข้าม condition และ recording pool ไม่ข้าม split
- Telephone: sample rate/length/finite, passband/stopband บนสัญญาณจำลอง, codec roundtrip และ config hash
- Training: gradients มีจริง, loss/output ถูกชนิด, save/reload/resume และไม่โหลด Final Test ระหว่าง train
- Metrics: scores perfect → EER 0%, reversed → EER 100%, constant/tied balanced scores → EER 50% ตาม interpolation ที่ประกาศ; one-label/nonfinite ต้อง error
- Threshold: prediction ที่ score เท่ากับ τ เป็น bonafide, finite endpoint candidates, threshold มาจาก Dev, ใช้ซ้ำข้าม Test condition
- Integrity: changed generator revision/config/checkpoint ทำให้ artifact ID เปลี่ยน, interrupted file ไม่ถูกนับ done, join ไม่ทำแถวพอง

### Integration / acceptance tests

1. tiny synthetic dataset ที่ไม่มีสิทธิ์ข้อมูลติดขัด รัน audit → split → mock TTS → conditions → train smoke → Dev threshold → Test metrics ได้ครบ
2. tiny real Train/Dev subset ที่ได้รับอนุญาต ตรวจ generator จริงและ adapter จริงทั้งสองตัว
3. score ชุดเดียวกันสองครั้งได้ผลตาม tolerance และจำนวนแถว/hash เดิม
4. Clean/Mixed คู่เดียวกันมี base sample schedule ตรงกันและต่างเฉพาะ condition ที่ออกแบบ
5. ผู้อื่นอ่าน run config + manifest hashes แล้ว reproduce metric จาก score CSV ได้ โดยไม่ต้อง retrain

ผล smoke test ต้องเขียนว่า smoke test ไม่ใช้กราฟ loss จากข้อมูลจิ๋วแทนผลวิจัย

<a id="s19"></a>
## 19. เครื่องส่วนตัว / Colab / พื้นที่ / การกู้คืน

### 19.1 แบ่งงานตามเครื่อง

- เครื่องส่วนตัว: audit/EDA/split, pilot, ทดสอบโค้ด และ training ขนาดเล็กเท่าที่วัดแล้วทำได้
- GPU training/TTS หนัก: ใช้เครื่องที่มีทรัพยากรเพียงพอหรือ Colab หากสิทธิ์ข้อมูลอนุญาต ก่อนอัปโหลดต้องตรวจเงื่อนไขแหล่งข้อมูลและบัญชีปลายทาง
- `.venv` คือ environment บน disk เครื่องที่รัน ไม่ใช่พื้นที่ชั่วคราวแบบ Colab runtime
- ใน Colab `/content` เป็นพื้นที่ runtime ไม่ใช้เป็นที่เก็บถาวร ต้องมีวิธี sync artifacts/checkpoints ไป storage ที่อนุญาตและตรวจ hash หลัง copy
- VS Code ใช้เป็น editor ได้ แต่ location ของข้อมูลขึ้นกับ kernel/runtime ที่เลือก ไม่ใช่หน้าตา editor ต้องตรวจ `cwd`, device และ data root ทุกครั้ง

### 19.2 ประมาณพื้นที่ก่อนสร้างเสียงหลัก

- mono 16 kHz PCM16 ใช้ประมาณ 32,000 bytes/วินาที หรือ 115.2 MB/ชั่วโมงก่อน overhead
- ถ้าเก็บ float32 PCM ใช้ประมาณสองเท่า; FLAC/MP3 มีขนาดแปรตามข้อมูล ไม่ใช้สูตร PCM เป็นขนาด archive จริง
- รวม original Common Voice + native TTS + canonical + Dev/Test condition cache + checkpoints/optimizer states + outputs
- Train augmentation แนะนำสร้าง on-the-fly เพื่อไม่เก็บ noise versions จำนวนมาก
- pilot วัดขนาดต่อชั่วโมงของ format ที่ใช้จริง แล้วคำนวณ expected total พร้อมเผื่อพื้นที่ temporary/checkpoints
- SEA-Spoof/Typhoon local data ถูกล้างตามคำขอแล้ว สำหรับข้อมูลใหม่/checkpoints/งานทีม ห้ามลบเพื่อเอาพื้นที่โดยอนุมานเอง ต้องตรวจขอบเขตคำสั่งและเป้าหมายให้ชัด

### 19.3 Resume / failure handling

- synthesis ใช้ job ledger, training ใช้ last checkpoint; สองส่วนเป็นคนละ state
- ถ้าเครื่องดับ/Colab หลุด ต้องตรวจ output integrity ก่อน resume ไม่ถือว่าไฟล์ที่มีชื่อแล้วสมบูรณ์
- ใช้ temporary files + atomic rename และไม่ให้สอง process เขียน run/job เดียวกันพร้อมกัน
- บันทึก logs โดยไม่พิมพ์ access token, private path ที่ไม่จำเป็น หรือข้อมูลส่วนบุคคลลง public report
- ไม่เก็บ token ใน notebook output/config ที่ commit; ใช้ credential mechanism ของแหล่งข้อมูล
- เก็บ immutable data/checkpoint hashes นอก runtime ชั่วคราว ทำ backup เฉพาะปลายทางที่ได้รับอนุญาต

<a id="s20"></a>
## 20. คำสั่งที่มีแล้วและคำสั่งที่ต้องสร้าง

### 20.1 คำสั่งที่มีใน repository ปัจจุบัน

เปิด PowerShell ที่ project root แล้วตรวจสถานะแบบไม่แก้ข้อมูล:

```powershell
git status --short --branch
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe -m thai_spoof.cli --help
.\.venv\Scripts\python.exe -m thai_spoof.cli evaluate --help
```

`infer` / `evaluate` ของเดิมใช้ตรวจ baseline inference ได้ แต่ **ยังไม่ใช่ pipeline ฝึก/ประเมิน Final Test ตามเอกสารนี้** โดยเฉพาะ threshold ต้องแก้ก่อน อย่ารัน `setup.ps1` เพื่อเริ่มแผนนี้โดยอัตโนมัติ

### 20.2 CLI contract ที่เสนอให้ AI ผู้รับช่วงพัฒนา

> คำสั่งด้านล่างเป็น **specification ของคำสั่งใหม่ที่ยังต้องเขียน** ไม่ใช่สิ่งที่รับประกันว่ารันได้ตอนนี้ ผู้พัฒนาต้องทำ `--help`, validation, dry-run ที่เหมาะสม และ integration tests ก่อนแนะนำให้ผู้ใช้รัน

ใช้ dispatcher `experiments/research/scripts/cvtts_pipeline.py` เรียก modules ใน `src/thai_spoof/cvtts/` โดยให้ common options ได้แก่ `--config`, `--dry-run` สำหรับงานเขียนข้อมูล และ `--output-root` สำหรับ override ที่บันทึกใน resolved config

| Subcommand | Input / หน้าที่ | Output / ข้อจำกัด |
| --- | --- | --- |
| `audit` | Common Voice root/release | metadata + audio QC report; ไม่แก้ raw files |
| `split` | eligible manifest + split policy | split assignments / leakage checks / hashes |
| `tts-pilot` | Train pilot text + registry | candidate outputs / cost / QC worksheet |
| `generate` | frozen split texts + selected generator | native TTS + resumable ledger |
| `prepare` | source real/TTS + locked QC/audio rules | base manifest / canonical audio / retention |
| `conditions` | base Dev/Test + noise pools | deterministic condition manifests/cache |
| `validate` | manifests/config/artifacts | fail-fast report ตาม gates ที่เลือก |
| `train` | resolved run config | checkpoints / train log / Dev metrics; ไม่รับ Final Test |
| `score` | explicit checkpoint + manifest | raw scores; แยกจากการตั้ง threshold |
| `select-threshold` | Dev scores เท่านั้น | threshold.json ที่ผูก checkpoint/Dev hash |
| `evaluate` | scores + Dev threshold | EER + fixed-threshold metrics; ไม่เลือก recipe |
| `report` | metric files / lock manifest | tables/plots/sanitized Markdown summary |

ตัวอย่างลำดับ **หลัง implement commands แล้ว**:

```powershell
# ตรวจข้อมูลและแบ่งชุด
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py audit --config experiments\research\configs\protocol_v1.yaml
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py split --config experiments\research\configs\protocol_v1.yaml

# ทดลอง/สร้าง TTS; dispatcher ต้องเรียก environment ที่ registry ระบุ
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py tts-pilot --config experiments\research\configs\protocol_v1.yaml --generator G1
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py generate --config experiments\research\configs\protocol_v1.yaml --generator G1 --resume

# เตรียม shared inputs และตรวจ gates; G2 ต้องสร้างครบก่อน prepare core cohort
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py prepare --config experiments\research\configs\protocol_v1.yaml
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py conditions --config experiments\research\configs\protocol_v1.yaml --split dev
# ต้องรัน unit tests และ tiny training/gradient/reload smoke ตามส่วน 14.1 ผ่านก่อน Gate 6
# validate ต้องอ่านหลักฐานการทดสอบด้วย ไม่ใช่ตรวจ manifest อย่างเดียวแล้วถือว่าผ่าน
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py validate --config experiments\research\configs\protocol_v1.yaml --through-gate 6

# ตัวอย่างหนึ่ง run; ต้องสร้าง resolved configs ให้ครบทุก model/arm/seed
.\.venv\Scripts\python.exe experiments\research\scripts\cvtts_pipeline.py train --config configs\cvtts\runs\aasist_clean_seed13.yaml
```

คำสั่ง `score/select-threshold/evaluate` ต้องรับ path ของ artifact ที่มีจริงอย่างชัดเจน เช่น `--checkpoint`, `--manifest`, `--scores`, `--threshold`, `--output` และตรวจ hash/split ไม่ใช้ค่าปริยายที่เผลอหยิบ pretrained weights หรือ Test มาเลือก threshold

### 20.3 ตัวอย่าง config เชิงสัญญา — ยังต้องเติมและ validate

```yaml
protocol_id: cvtts_v1_draft
status: draft
dataset_version: cvtts_001
common_voice:
  release: REQUIRED_EXACT_RELEASE
  locale: th
  root: REQUIRED_LOCAL_DATA_ROOT
  metadata: validated.tsv
split:
  seed: 20261002
  target_ratios: [0.8, 0.1, 0.1]
  isolation: [speaker, normalized_text, duplicate_audio, lineage]
cohort:
  target_real: {train: 6000, dev: 1000, test: 1000}
  one_real_per_text: true
  max_clips_per_speaker: 50
  duration_s: {min: 1.0, max: 15.0}
  require_complete_seen_generator_bundle: true
audio:
  sample_rate: 16000
  input_samples: 64600
  train_crop: random_inclusive
  eval_crop: first
  short_audio: repeat
  pipeline_version: canonical_window_condition_v1
tts:
  registry: configs/cvtts/tts_registry.yaml
  seen: [G1, G2]
  held_out: [] # เพิ่ม G3 เฉพาะเมื่อพร้อมและล็อกก่อนเลือก detector
conditions:
  mixed_probabilities: {clean: 0.3333333333, noise: 0.3333333333, telephone: 0.3333333334}
  train_noise_snr_db: [0, 10, 20]
  dev: [clean, noise_10db, telephone_v1]
  test: [clean, noise_20db, noise_10db, noise_0db, telephone_v1]
  noise_manifest: REQUIRED_SPLIT_NOISE_MANIFEST
training:
  models: [aasist, rawnet2]
  arms: [clean, mixed]
  seeds: [13, 37, 73]
  optimizer: adamw
  learning_rate: 0.00001
  weight_decay: 0.0001
  microbatch: 2
  accumulation_steps: 8
  max_optimizer_updates: 2000
  dev_every_updates: 100
  checkpoint_selection: mean_dev_condition_eer
evaluation:
  score_type: bonafide_margin_v1
  eer_method: roc_linear_crossing_v1
  threshold_source: pooled_dev_equal_condition_weight
  decision: bonafide_if_score_greater_equal_threshold
```

validation ต้องปฏิเสธ `REQUIRED_*`, unresolved revisions, source paths ที่หาย, missing licenses/checkpoint hashes และ `status: draft` สำหรับ main experiment; pilot ต้องสั่งโหมด pilot โดยชัดเจน ผู้พัฒนาต้องเพิ่ม config ของ filter/QC/precision/RNG/checkpoints ตามส่วนอื่นให้ครบก่อน lock ไม่ถือว่า YAML ตัวอย่างนี้ครอบคลุมรายละเอียดทุกตัวแล้ว

<a id="s21"></a>
## 21. แผนงานย่อยสำหรับทีมและ AI ผู้รับช่วง

### 21.1 Backlog ตามลำดับ dependency

| ID | งาน | ขึ้นกับ | ผลส่งมอบและเกณฑ์จบ |
| --- | --- | --- | --- |
| T00 | ยืนยัน scope/decision log/environment | ไม่มี | Gate 0, ไม่มีเปลี่ยน package/data โดยพลการ |
| T01 | config schema/provenance/ignore rules | T00 | parse/validate, secrets/data ไม่ขึ้น Git |
| T02 | Common Voice audit + notebook | T01 | Gate 1, อ่าน raw อย่างเดียว |
| T03 | split + leakage tests | T02 | Gate 2, deterministic manifests |
| T04 | TTS adapters + pilot report | T03 | G1/G2 ผ่าน Gate 3, registry pin ครบ |
| T05 | generator queue/resume/QC | T04 | small corpus end-to-end ก่อน bulk |
| T06 | bulk synthesis/base corpus | T05 | Gate 4, immutable manifest version |
| T07 | shared audio/noise/telephone | T01, T03 | synthetic tests + Gate 5 เมื่อมี corpus |
| T08 | score/metrics/threshold contracts | T01 | unit tests ส่วน 13/18 ผ่าน |
| T09-A | AASIST training adapter | T07, T08 | gradient/save-load/smoke ผ่าน |
| T09-R | RawNet2 training adapter | T07, T08 | gradient/save-load/smoke ผ่าน |
| T10 | tiny integrated run + trainer resume | T05, T07, T08, T09 | Gate 6, ตรวจ checkpoint จริง |
| T11 | training pilot / lock recipe | T06, T10 | cost estimate + fixed recipe ก่อน main |
| T12 | main runs และ Dev thresholds | T11 | Gate 7, ทุก run ครบตามงบ |
| T13 | Final Test scoring + analysis | T12 | Gate 8, no test-driven selection |
| T14 | report/reproducibility package | T13 | ผล/ข้อจำกัด/คู่มือครบตามส่วน 16 |

งานที่ทำขนานได้: T07/T08 ระหว่างเตรียม TTS; T09-A/T09-R แยกทีมหลัง contract กลางนิ่ง; EDA/report writing ทำต่อเนื่อง แต่ไม่ให้หลายคนแก้ manifest หลักหรือ metrics convention โดยไม่มี review

### 21.2 ข้อกำหนดสำหรับ AI ผู้รับช่วง

1. อ่านไฟล์นี้ครบและตรวจโค้ดจริงก่อนสรุปสถานะ ไม่เชื่อว่าคำสั่ง proposed มีอยู่แล้ว
2. แยกงานที่ “ทำเสร็จ/ตรวจแล้ว/ยังไม่ได้รัน/ติด blocker” ในคำตอบทุกช่วง
3. เริ่มทีละ task ที่มี dependency พร้อม พร้อมบอกไฟล์ที่จะสร้าง/แก้และเกณฑ์ตรวจ
4. ไม่โหลด corpus ใหม่/ติดตั้งทุก TTS/เปิดงานฝึกยาวพร้อมกันเพียงเพราะเอกสารมีแผนทั้งโครงการ ต้องยึดคำสั่งผู้ใช้และทรัพยากรในรอบนั้น
5. ไม่ลบ Common Voice, noise, TTS corpus, checkpoint หรือไฟล์เพื่อนโดยอนุมานว่าไม่ใช้แล้ว; cleanup ของข้อมูลเก่าทำตามคำขอที่บันทึกไว้ ไม่ใช่สิทธิ์ให้ลบข้อมูลใหม่ในอนาคต
6. ไม่แก้ label, split, generator revisions, test cohort หรือ threshold policy เพื่อให้คะแนนดีขึ้นโดยไม่มี decision log และ protocol version
7. ไม่ใช้ผล Test ย้อนเลือกการทดลอง และไม่ใช้คำว่า train สำเร็จถ้าเพียงรัน pretrained inference
8. ไม่เดา feature names, release, จำนวนคน, licensing, memory หรือ training times ถ้ายังไม่ตรวจ
9. แก้ shared source/tests เป็นงานเล็กที่ review ได้ รักษาความเข้ากันได้ของ CLI เดิม
10. ห้าม commit/push ให้ผู้ใช้เอง ใช้ branch ที่ไม่มี `codex/` และรักษางานที่มีอยู่
11. เก็บรหัส/เสียง/metadata รายบุคคลเป็น private artifacts และสรุปเฉพาะที่ได้รับอนุญาตเผยแพร่
12. เมื่อจบแต่ละ task ให้แนบ changed files, verification commands/results, remaining risks และ next task

### 21.3 Prompt เริ่มงานที่ส่งให้โมเดลอื่นได้

```text
อ่าน docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md ทั้งไฟล์ก่อนลงมือ
นี่คือแผนหลักฉบับใหม่: Common Voice Thai → หลาย TTS → fine-tune AASIST/RawNet2
เปรียบเทียบ Clean กับ Clean+Noise+Telephone; SEA-Spoof/Typhoon ถูกนำออกแล้ว ไม่ต้องกู้คืน
อย่าเริ่มทั้งโปรเจกต์พร้อมกัน ให้ทำ T00–T02 ก่อน:
1. ตรวจ Git/คำสั่ง repository/สภาพแวดล้อมและที่อยู่ Common Voice แบบ read-only
2. ตรวจ exact release/schema/สิทธิ์และจำนวน metadata/audio ที่มีจริง
3. เสนอ decision log, config/data schema, ignore rules และ Common Voice audit notebook
4. พัฒนาเฉพาะขั้น audit ที่ตกลง พร้อม tests และรายงานสิ่งที่ตรวจได้จริง
อย่าดาวน์โหลดข้อมูลก้อนใหญ่ ติดตั้ง TTS เทรน ลบข้อมูล หรือใช้ Final Test เลือกวิธีในรอบแรก
อย่า commit/push ผู้ใช้จะทำเอง และใช้ชื่อ branch ที่ไม่ขึ้นต้น codex/
ถ้าข้อมูลหรือการตัดสินใจสำคัญยังขาด ให้รายงานช่องว่าง ไม่แต่งตัวเลขหรือเดา release
แยกคำสั่ง existing ออกจาก proposed และรายงานวิธีตรวจงานก่อนส่งต่อ T03
```

### 21.4 สิ่งที่ผู้ใช้ควรเตรียมสำหรับรอบถัดไป

- ตำแหน่ง Common Voice ที่มีจริง และหลักฐาน release/download page ที่ใช้
- คำตอบอาจารย์/เพื่อนเรื่อง fixed experiment vs adaptive loop, TTS vs cloning, demographic scope
- พื้นที่ว่างและเครื่องที่จะใช้สร้างเสียง/ฝึก รวมสิทธิ์ใช้ Colab/remote storage หากเกี่ยวข้อง
- งบเวลา/จำนวนข้อมูลที่รับได้ ไม่จำเป็นต้องทราบค่าที่ดีที่สุดก่อน pilot

ถ้ายังไม่มีคำตอบครบ เริ่ม read-only audit ได้ก่อน ไม่ต้องหยุดการอ่านทฤษฎีหรือสำรวจสิ่งที่มี

<a id="s22"></a>
## 22. คำถามที่พบบ่อยและคำอธิบายให้อาจารย์

**ทำไมต้องศึกษาทฤษฎีก่อน?** เพื่อแยกให้ได้ว่าอะไรสร้างเสียง อะไรตรวจเสียง, TTS ต่างจาก cloning อย่างไร, noise/codec กระทบสัญญาณแบบไหน และ metric วัดอะไร มิฉะนั้นอาจทำโค้ดได้แต่ตอบข้อจำกัดของการทดลองไม่ได้

**ทำไมหลาย TTS ยังอาจ overfit?** เพราะ detector อาจจำ artifact ของ generator, codec หรือ preprocessing ที่เห็น การมีหลายแหล่งเป็นแนวทางเพิ่มความหลากหลาย แต่ต้องวัดด้วยข้อมูลแยกและ held-out generator จึงจะรู้ว่าช่วย generalization เพียงใด

**ทำไมไม่ปรับเสียงสูงต่ำอย่างเดียว?** เพราะ pitch variation ยังมาจาก generator เดิมและอาจเพิ่ม artifact ของการดัดแปลง ถ้าจะวิจัยผล pitch ต้องเพิ่ม ablation และคุมตัวแปร ไม่ใช้แทนการเปรียบเทียบ Clean/Mixed

**ทำไม 4 วินาที?** เป็นขนาด window 64,600 samples ที่โครงงานเสนอใช้ให้ทั้งสองระบบเทียบกันได้ ภายใต้ 16 kHz เท่ากับ 4.0375 วินาที ไม่ใช่ข้อจำกัดว่าไฟล์ยาวกว่านี้โหลดไม่ได้ และไม่ได้แปลว่า architecture ทั้งสองต้องใช้ window นี้ในทุกงาน

**Noise+Telephone หมายถึงใส่สองอย่างพร้อมกันไหม?** ใน v1 นี้ไม่ใช่ หมายถึงฝึกด้วยสาม condition: clean หรือ noise หรือ telephone ถ้าต้องการ noise แล้วผ่านโทรศัพท์ด้วยให้เพิ่ม condition แยก

**ยังใช้ SEA-Spoof/Typhoon ไหม?** ไม่ใช้ใน workflow ปัจจุบัน และลบ local data/EDA/pipelines ที่เกี่ยวข้องตามคำขอแล้ว หากอนาคตต้องการ external evaluation ให้ถือเป็นการเพิ่ม scope ใหม่พร้อมตรวจสิทธิ์/ดาวน์โหลดใหม่ ไม่ใช่ dependency ของแผนนี้

**ต้องวนผล Test ไปสร้างเสียงใหม่ไหม?** ไม่ใช่ค่าเริ่มต้นของแผน ถ้าต้องปรับวนให้ใช้ Dev และมี control/budget ชัดเจน ส่วน Final Test เก็บไว้ประเมินหลังจบการพัฒนา

**AASIST และ RawNet2 ใครดีกว่า?** ยังตอบจากชื่อไม่ได้ ต้องรายงานผลภายใต้ข้อมูล/checkpoint/งบเดียวกันตามที่คุมได้ อ่าน paper เพื่ออธิบายกลไกและข้อจำกัด ไม่ตัดสินว่าระบบใหม่กว่าต้องชนะทุก condition

ตัวอย่างอธิบายแบบภาษาพูด:

> “ตอนนี้ปรับแผนมาใช้ Common Voice ภาษาไทยเป็นเสียงจริงและแหล่งข้อความครับ แล้วนำข้อความไปสร้างเสียงสังเคราะห์ด้วย TTS หลายระบบ จากนั้น fine-tune AASIST และ RawNet2 คนละสองแบบ คือใช้เสียงที่ไม่ได้เติมสภาพแวดล้อมจำลอง กับใช้ทั้ง clean เสียงรบกวน และโทรศัพท์จำลอง เราจะแบ่งผู้พูด ข้อความ และข้อมูลต้นทางออกจากกันก่อนสร้างเสียง เพื่อไม่ให้ข้อมูลรั่ว ใช้ Dev เลือกโมเดลและ threshold แล้วใช้ Test ที่เก็บไว้เปรียบเทียบ EER ว่าการฝึกหลาย condition ช่วยจริงหรือไม่ ส่วนการวนกลับไปปรับ TTS และการวิเคราะห์อายุเพศถิ่นยังต้องยืนยันขอบเขตเพิ่มเติมครับ”

<a id="s23"></a>
## 23. แหล่งอ้างอิงและข้อจำกัด

แหล่งด้านล่างใช้ประกอบการวางแผน ณ วันที่จัดทำ ผู้พัฒนาต้องตรวจ revision/terms ปัจจุบันและเวอร์ชันที่ใช้จริงอีกครั้งก่อนดาวน์โหลด/ใช้งาน ไม่ใช้ลิงก์ล่าสุดแทนการบันทึก artifact revision

### Dataset / สิทธิ์

- [Common Voice dataset repository และเอกสารโครงสร้าง](https://github.com/common-voice/cv-dataset)
- [ตัวอย่างหน้า Common Voice Thai บน Mozilla Data Collective](https://mozilladatacollective.com/datasets/cmu5x5tj000f2nq0755h8qcy5) — ไม่ใช่การยืนยันว่าไฟล์ในเครื่องเป็น release ของหน้านี้
- [Mozilla Data Collective: ข้อจำกัดการ re-host/share](https://community.mozilladatacollective.com/faq-why-cant-i-re-host-or-share-common-voice-datasets-that-i-download-from-mdc/) — แยก license เนื้อหาออกจากเงื่อนไขการเข้าถึง/แบ่งปันที่ตกลงไว้
- [MUSAN ที่ OpenSLR](https://www.openslr.org/17/) — ตรวจ license และเลือก noise subset ที่ตรง scope

### TTS candidates / ทฤษฎี

- [MMS Thai model card](https://huggingface.co/facebook/mms-tts-tha) และ [Transformers VITS documentation](https://huggingface.co/docs/transformers/model_doc/vits)
- [Wayu Paxa TTS Edge model card](https://huggingface.co/wayu-ai/wayu-paxa-tts-edge), [inference repository](https://github.com/wayu-research/wayu-tts-inference), [terms](https://www.wayuresearch.org/terms)
- [Lunarlist Thai TTS model card](https://huggingface.co/lunarlist/tts-thai-last-step), [PyThaiTTS](https://github.com/PyThaiNLP/PyThaiTTS), [ThaiTTS ONNX](https://github.com/PyThaiNLP/thaitts-onnx)
- [Khanomtan TTS v1.1](https://huggingface.co/wannaphong/khanomtan-tts-v1.1)
- [FastSpeech 2 paper](https://arxiv.org/abs/2006.04558) — ใช้ศึกษาการสร้างเสียง/variance control ไม่ใช่การบอกว่ามี Thai checkpoint พร้อมใช้ในโครงงานนี้

### Detector / protocol / metrics

- [AASIST paper](https://arxiv.org/abs/2110.01200) และ [official implementation](https://github.com/clovaai/aasist)
- [RawNet2 anti-spoofing paper](https://arxiv.org/abs/2011.01108) และ [ASVspoof 2021 official baseline repository รวม RawNet2](https://github.com/asvspoof-challenge/2021)
- [ASVspoof 2021 evaluation plan](https://www.asvspoof.org/asvspoof2021/asvspoof2021_evaluation_plan.pdf) และ [official evaluation metrics code](https://github.com/asvspoof-challenge/2021/blob/main/eval-package/eval_metrics.py)
- [scikit-learn: data leakage / common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
- [GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html) — group split อย่างเดียวไม่รับประกัน text isolation ต้องตรวจตามส่วน 9
- [ROC curve conventions](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html)
- [FFmpeg codec documentation](https://ffmpeg.org/ffmpeg-codecs.html) — ตรวจ capabilities ของ build ที่ใช้จริงด้วย

### หมายเหตุปิดท้าย

แผนนี้ให้ลำดับงานและค่าเริ่มต้นที่นำไปพัฒนาได้ แต่ไม่ได้แทนการอนุมัติขอบเขตจากอาจารย์ การตรวจสิทธิ์เฉพาะ release หรือ feasibility pilot บนเครื่องจริง หากต้องเปลี่ยนข้อเสนอ ให้บันทึกว่าเปลี่ยนอะไร เพราะอะไร ก่อนหรือหลังเห็น Dev/Test และออก protocol/data version ใหม่เมื่อกระทบการเปรียบเทียบ
