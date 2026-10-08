# Decision log

## 3 ตุลาคม 2026 — ปรับขอบเขตและจัด repository

- ตามความเข้าใจล่าสุด ใช้ Common Voice Thai + TTS เป็นแกนหลัก เปรียบเทียบ AASIST/RawNet2 แบบ Clean และ Mixed
- ผู้ใช้อนุญาตให้ลบข้อมูล/โค้ด/เอกสารที่ไม่ใช้แล้ว จึงนำ SEA-Spoof/Typhoon pipelines และ local datasets เก่าออก ไม่เก็บ archive ซ้ำใน project
- คง package และ pretrained weights ของสอง detector เพราะยังใช้ต่อ ไม่ย้ายเส้นทาง model เพียงเพื่อเปลี่ยนชื่อโฟลเดอร์
- Manifest จริงอยู่ใต้ `data/processed/cvtts/<version>/manifests/`; ตัวอย่างที่แจกได้อยู่ `examples/`
- ยังไม่มีการดาวน์โหลดข้อมูลใหม่ สร้าง TTS หรือ fine-tune ในการปรับโครงสร้างครั้งนี้
- ผู้ใช้ commit เอง; branch ของงานนี้คือ `refactor-common-voice-layout`

## 7 ตุลาคม 2026 — AASIST Clean feasibility smoke

- หลัง canonical pilot เพิ่ม shared window/Dataset และ script 1-epoch smoke; ใช้ Train 160 / Dev 40, Wayu ตัวเดียว เพื่อพิสูจน์ forward/backward/update/reload ไม่ใช่ scope หลักหลาย TTS
- อิง baseline input 64,600 samples; Train random inclusive crop / Dev first / short repeat ไม่เปลี่ยน full canonical files หรือ native audio
- ใช้ AdamW 1e-5, microbatch 2, accumulation 8, unweighted cross-entropy, float32; ไม่เพิ่ม condition จำลอง ไม่ resume/best selection/Test
- Preflight 4 Train clips 1 update ผ่าน จากนั้น full epoch เริ่มจาก pretrained เดิมใหม่ 160 clips / 10 updates และ fresh-model reload ผ่าน
- Dev loss เพิ่ม 1.594355 → 4.853433; ผ่านด้านเทคนิคเท่านั้น ไม่อ้างว่าความแม่นยำเพิ่ม ขั้นต่อไปคือ overfit-small-batch/recipe checks ก่อนขยาย corpus/conditions
- Branch `feat-aasist-clean-smoke` แยกจาก canonical audio ที่ผู้ใช้ commit แล้ว; ผู้ใช้ commit/push เอง รายละเอียดและคำสั่งอยู่ [คู่มือ](../../experiments/pilot/docs/aasist/AASIST_CLEAN_SMOKE_TH.md)

## 7 ตุลาคม 2026 — Fixed Train subset memorization check

- ทำขั้นถัดไปใน pilot: Train 2 paired texts / 4 clips (2 real + 2 Wayu), seeded selection และ fixed windows ไม่เลือกด้วยคะแนน detector ไม่ใช้ Dev/Test
- เริ่ม pretrained เดิมใหม่; eval mode WITH autograd, dropout off/BN running stats frozen แต่ทุก parameter trainable; AdamW 1e-4/weight decay 0, microbatch 2/effective batch 4
- ตั้งเกณฑ์ก่อนรัน accuracy=100% และ CE<=0.1 หลังอย่างน้อย 20 updates, งบสูงสุด 100; ผ่านที่ update 20, loss 3.375760→0.002260, fresh-model reload ตรงกัน
- เป็น memorization diagnostic ไม่ใช่ generalization/main recipe/สาเหตุของ Dev loss เดิม ไม่ใช้ checkpoint นี้เป็นจุดเริ่ม main run
- พบ Git checkout เปลี่ยน code LF เป็น CRLF ทำให้ preparation hashes ไม่ตรงก่อนฝึก จึงเพิ่มตัวตรวจที่ยอมรับเฉพาะ CRLF→LF พร้อม log; audio/manifests/hash reports/results เก่าไม่ถูกแก้
- Branch `feat-aasist-overfit-check` ต่อจาก main; ผู้ใช้ commit/push เอง ดู [รายละเอียด](../../experiments/pilot/docs/aasist/AASIST_OVERFIT_CHECK_TH.md)

## 7 ตุลาคม 2026 — แยก pilot / research layout

- รวม notebooks/scripts/guides ที่รัน pilot ไว้ `experiments/pilot/`; `experiments/research/` มี README สถานะแผน ยังไม่มี main trainer
- แยก Dataset/overfit เฉพาะ pilot ไป `src/thai_spoof/pilot/` และ tests ไป `tests/pilot/`; network/common helpers อยู่ตำแหน่งเดิม
- ย้ายผลเดิมทั้ง folder ไป `results/pilot/` และ executed notebooks ไป `experiments/pilot/notebooks/outputs/` ไม่แก้ผล/hashes เก่าว่าเป็น run ใหม่
- ไม่ย้าย raw/canonical/native audio หรือ pretrained weights; source code paths ของ historical runs ตรวจด้วย Git ก่อน refactor
- แก้ canonical notebook code hash ให้ normalize CRLF→LF เพื่อรันซ้ำหลัง Git checkout โดยไม่เปลี่ยน existing report; audio/manifest hashes ยังคง byte-exact
- มีหน้าเริ่มเดียว `experiments/pilot/README.md` แสดงขั้นที่ทำแล้ว/ขั้นถัดไป; Branch `refactor-pilot-research-layout` ผู้ใช้ commit/push เอง

## 8 ตุลาคม 2026 — คู่ตรวจโหมด BatchNorm ใน AASIST pilot

- Branch `feat-aasist-bn-diagnostic` จาก main ที่ผู้ใช้ commit โครงสร้างแยกโมเดลแล้ว ไม่ commit/push อัตโนมัติ
- ทำสอง Clean epochs ใหม่จาก pretrained เดิม: microbatch 2/accumulation 8, LR 1e-5, seed/data/crops/order เท่ากัน เปลี่ยนเฉพาะ BN train vs frozen; dropout ยัง train และ BN affine ยัง trainable
- Frozen BN ใช้สถิติ pretrained normalize Train ด้วย ไม่ใช่เพียงหยุด running-buffer EMA และไม่ใช่ eval ทั้งโมเดลแบบการจำ 4 คลิป
- คู่ `bn_pair_20261008_v1`: Dev loss เริ่ม 1.594355 ทั้งคู่; Train BN หลังฝึก 4.853433, Frozen BN 1.074124; controls/BN buffers/fresh-model reload ผ่าน
- ผลสนับสนุนให้ศึกษา Frozen BN ต่อใน Train/Dev แต่ยังไม่ล็อก main recipe/อ้างสาเหตุทั้งหมดหรือ Test accuracy/EER เป็นเพียง seed เดียว/1 epoch/Wayu ระบบเดียว
- เก็บผลใน `results/pilot/aasist_bn_diagnostic/` ไม่แก้ data/pretrained/old runs/handoff ZIP; อ่าน [คู่มือและผล](../../experiments/pilot/docs/aasist/AASIST_BATCHNORM_CHECK_TH.md)

## 8 ตุลาคม 2026 — Frozen BN 3 epochs พร้อม learning curve

- ผู้ใช้อนุญาตให้ต่อจากคู่ BN โดยลอง 3 epochs กำหนดงบก่อนรัน เริ่ม pretrained เดิมใหม่ ไม่ต่อจาก checkpoint pilot เก่า
- เพิ่มสคริปต์แยก `train_aasist_frozen_bn.py` และ helper `learning_curve.py` ไม่แก้สคริปต์/ผล BN pair ที่ stage ไว้แล้ว
- ใช้ windows เดิมตลอด 3 epochs; recipe อื่นคงเดิม, dropout เปิดตอน Train, Frozen BN statistics คงเดิม; วัด Train/Dev ใน eval mode แยกจาก optimization loss
- Extra Train monitoring และ fresh-model reload ไม่เปลี่ยน RNG ฝึก; บันทึก checkpoint/ตรวจ reload ทุก epoch เลือก lowest Dev CE ของ epochs 1–3 เสมอกันเลือกแรก ไม่ใช้ Test และ epoch 0 เป็น reference เท่านั้น
- Run `frozen3_20261008_v1`: Train evaluation CE 1.785548→1.477809→0.972610→0.530635; Dev CE 1.594355→1.074124→0.642973→0.338209; BN buffers คงเดิม/reload logits ตรงกันทุก epoch
- ผลแสดง loss ลดลงในงบนี้ ไม่พิสูจน์ว่าไม่มี overfit/generalization หรือ best main recipe; ยังคง pilot/seed เดียว/Wayu ตัวเดียว และไม่ใช้ผลนี้แทน EER/Final Test
- ไม่เปลี่ยน branch/index/staging ของผู้ใช้ ไม่ commit/push อัตโนมัติ งานใหม่อยู่ใน working tree ของ `feat-aasist-bn-diagnostic` ดู [คู่มือและกราฟ](../../experiments/pilot/docs/aasist/AASIST_FROZEN_BN_CURVE_TH.md)

## 8 ตุลาคม 2026 — ตรวจสาม seeds บน pilot split เดิม

- Branch `feat-aasist-seed-check` จากงาน curve ล่าสุดที่ผู้ใช้ commit/push แล้ว ไม่ใช้ `codex/` ไม่ commit/push อัตโนมัติ
- กำหนดล่วงหน้า seeds 42/43/44 และ 3 epochs แต่ละ seed ใช้ 42 เดิมที่ตรวจผ่าน ฝึกใหม่เฉพาะ 43/44 จาก pretrained เดิม สูตร/Train/Dev เดิม เปลี่ยนเฉพาะ seed (crop/shuffle/dropout)
- เพิ่ม `--seed` default 42 และ range guard โดยไม่มี recipe change; source compatibility ของผลเก่ายอมรับเฉพาะ CLI extension สามจุดและ CRLF→LF ไม่แก้ historical reports ให้มี hash ใหม่
- Suite `seeds_20261008_v1`: epoch-3 Dev CE 0.338209/0.338875/0.404151; mean 0.360412, sample SD (`ddof=1`) 0.037881 รายงานทุก seed ไม่เลือก winner
- ทั้งสามมี Train/Dev loss ลดลงในสาม epochs; BN buffers คงเดิม/Dev logits เริ่มต้นตรงกัน/checkpoint reload ผ่าน controls ตรวจ recipe/data/pretrained/environment/source/artifact hashes
- สรุปเฉพาะความสม่ำเสมอใน pilot split เดิม ไม่ใช่ CI/Test/EER/cross-generator performance หรือ main recipe ที่ยืนยันแล้ว ก่อนขยายงานต้องกำหนด protocol/cohort/generators/compute budget
- ผลจริงอยู่ `results/pilot/aasist_seed_stability/` และรอบใหม่ 43/44 อยู่ `results/pilot/aasist_frozen_bn_curve/` ไม่ขึ้น Git; raw/canonical/native audio, pretrained, ผลเก่าและ ZIP ส่งต่อไม่เปลี่ยน ดู [คู่มือ/กราฟ](../../experiments/pilot/docs/aasist/AASIST_SEED_STABILITY_TH.md)

## ยังรอยืนยันก่อนล็อก protocol

- Common Voice exact release/root/สิทธิ์
- fixed experiment หรือ adaptive Dev loop; TTS-only หรือจำเป็นต้อง cloning
- ขอบเขต demographic analysis และ held-out generator
- generators/revisions, cohort size, noise pool, telephone profile, tuning/compute budget

ค่าตัวเลขใน workflow เป็นข้อเสนอสำหรับ pilot ไม่ใช่ผลหรือข้อตกลงที่อาจารย์อนุมัติแล้ว เมื่อมีคำตอบให้เพิ่มวันที่ ผู้ยืนยัน เหตุผล และผลกระทบต่อ protocol version
