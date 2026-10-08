# แผนผังโปรเจกต์ — แยก pilot / research / โค้ดร่วม

## ให้ดูชื่อหมวดก่อน

- **pilot** = ทดลองให้ระบบทำงานและตรวจวิธีฝึก ยังไม่ใช่ผลวิจัยหลัก
- **research** = การทดลองจริงตาม protocol ที่จะล็อกภายหลัง ตอนนี้ยังไม่เริ่ม
- **src** = โค้ดที่ใช้ทำงาน ไม่ใช่ผลการทดลอง
- **data/results/checkpoints** = ข้อมูล/ผล/weights ในเครื่องไม่เข้า Git แต่คู่มือ/`.gitkeep` เข้า Git เพื่อให้เพื่อนเห็นโครงสร้าง

```text
project/
├─ experiments/
│  ├─ pilot/                       ← งานที่เราทำอยู่ตอนนี้
│  │  ├─ README.md                 ← เปิดอันนี้ก่อน
│  │  ├─ notebooks/                ← EDA → TTS → เตรียมเสียง
│  │  │  └─ outputs/               ← notebook ที่รันแล้ว (ไม่เข้า Git)
│  │  ├─ scripts/
│  │  │  ├─ aasist/                ← ฝั่งผู้ทำ AASIST
│  │  │  │  ├─ train_aasist_clean.py
│  │  │  │  ├─ check_aasist_overfit.py
│  │  │  │  ├─ check_aasist_batchnorm.py
│  │  │  │  ├─ train_aasist_frozen_bn.py
│  │  │  │  └─ check_aasist_seed_stability.py
│  │  │  └─ rawnet2/               ← ฝั่งเพื่อน มี README ยังไม่มี trainer
│  │  └─ docs/
│  │     ├─ aasist/                ← คู่มือและผล AASIST
│  │     ├─ rawnet2/               ← พื้นที่คู่มือ RawNet2 ยังไม่มีผลฝึก
│  │     ├─ NOTEBOOK_DETAILS_TH.md ← ข้อมูล/notebooks ใช้ร่วมกัน
│  │     └─ PATH_MIGRATION_TH.md   ← ประวัติย้ายไฟล์
│  └─ research/
│     └─ README.md                 ← ยังเป็นแผน ไม่ใช่โค้ดฝึกพร้อมใช้
├─ src/thai_spoof/
│  ├─ aasist/                      ← adapter/config ของ AASIST
│  ├─ rawnet2/                     ← model/adapter ฝั่งเพื่อน
│  ├─ cvtts/                       ← audio/windows/text/hash helpers ร่วม
│  ├─ pilot/                       ← Dataset/diagnostics เฉพาะชุดเล็ก
│  ├─ cli.py                       ← inference/evaluate เดิม
│  └─ metrics.py                   ← metrics เดิม ไม่ใช่ Final Test protocol ใหม่
├─ tests/
│  ├─ pilot/                       ← tests เฉพาะงานทดลองเล็ก
│  └─ cvtts/                       ← tests ของ shared helpers
├─ data/
│  ├─ raw/common_voice/
│  │  └─ cv-corpus-27.0-2026-09-11/th/
│  │     ├─ *.tsv                 ← metadata จริง ไม่เข้า Git
│  │     └─ clips/*.mp3            ← เสียงต้นทาง ห้ามแก้ in-place ไม่เข้า Git
│  ├─ processed/cvtts/pilot_v1/     ← ข้อมูลร่วมสองโมเดล ไม่ใช่ corpus วิจัยหลัก
│  │  ├─ canonical/clean16k/
│  │  │  ├─ train/bonafide/        ← WAV เสียงคน 80 คลิป
│  │  │  ├─ train/spoof/           ← WAV Wayu 80 คลิป
│  │  │  ├─ dev/bonafide/          ← WAV เสียงคน 20 คลิป
│  │  │  └─ dev/spoof/             ← WAV Wayu 20 คลิป
│  │  ├─ native_tts/
│  │  │  ├─ wayu/train/, wayu/dev/ ← เสียง Wayu ก่อนแปลง sample rate
│  │  │  └─ mms_tha/train/         ← ผลลอง MMS ไม่ใช่ corpus detector ปัจจุบัน
│  │  ├─ manifests/               ← CSV รายการข้อมูล/label/paths/hash (ไม่เข้า Git)
│  │  └─ qc/
│  │     ├─ canonical_audio/       ← รายงานเตรียม WAV
│  │     ├─ tts_experiments/       ← รายงานสร้างเสียง
│  │     ├─ tts_reviews/batches/   ← ข้อมูลตรวจตัวอย่างที่มีอยู่ ไม่เพิ่มความเห็นใหม่
│  │     └─ tts_samples/           ← รายงานลอง TTS
│  ├─ raw/noise/                   ← ยังไม่ได้เตรียม noise สำหรับการทดลองหลัก
│  └─ sample/                      ← เสียงลอง inference ไม่ใช่ชุด train/test
├─ results/
│  └─ pilot/
│     ├─ aasist_clean_smoke/       ← ผล Train 160 / Dev 40
│     ├─ aasist_overfit_check/     ← ผลจำ Train 4 คลิป
│     ├─ aasist_bn_diagnostic/     ← เปรียบเทียบโหมด BN บน Train/Dev
│     ├─ aasist_frozen_bn_curve/   ← Frozen BN 3 epochs / curves / checkpoint แต่ละ epoch
│     ├─ aasist_seed_stability/    ← สรุป seeds 42/43/44 ทั้งหมด ไม่เลือก winner
│     ├─ rawnet2/                  ← พื้นที่เพื่อน ยังไม่มี run
│     └─ share/                    ← ZIP ส่งในทีม ไม่เข้า Git
├─ checkpoints/                   ← weights ไม่ใช่ dataset; ไฟล์จริงไม่เข้า Git
│  ├─ aasist/AASIST.pth
│  ├─ rawnet2/pre_trained_DF_RawNet2.pth
│  └─ tts/                        ← MMS/Wayu สำหรับสร้างเสียง ไม่ใช่ detector
├─ external/aasist/               ← โครงข่ายต้นทางที่ยังใช้จริง
├─ scripts/                       ← setup/environment/smoke inference เท่านั้น
├─ configs/cvtts/                 ← dependencies ของ TTS pilot; ยังไม่มี main-run config
├─ docs/                          ← ภาพรวม/workflow/decisions/TEAM_HANDOFF_TH.md
└─ tmp/                           ← ชั่วคราว; tmp/wayu-python เป็น base ของ .venv-wayu อย่าลบ
```

## ไฟล์ที่ใช้ตอนนี้

เปิด [Pilot README](../experiments/pilot/README.md) มีลำดับ notebook/คำสั่งและสถานะครบ ไม่ต้องไล่เปิดทุกไฟล์ใน src

Raw Common Voice, canonical dataset และ notebook เตรียมข้อมูลใช้ร่วมกัน ไม่แยกสำเนาตาม AASIST/RawNet2 **pretrained weights แยกตามโมเดล** ห้ามใช้ weights ข้ามกัน ส่วนชุดข้อมูล/run สำหรับงานวิจัยจริงต้องสร้างเป็น version ใหม่ ไม่ตั้งชื่อ pilot_v1 เป็นงานจริงเฉย ๆ

แผนผังแสดงตำแหน่ง/ชนิดไฟล์ ไม่ใช่คำยืนยันว่า clone แล้วจะมีไฟล์จริงครบ โฟลเดอร์ที่ไม่ส่งข้อมูลเก็บ README/`.gitkeep` ไว้ใน Git เท่านั้น ดู [วิธีส่งต่องาน](TEAM_HANDOFF_TH.md)

## ย้ายอะไรบ้าง

| เดิม | ใหม่ |
| --- | --- |
| `data/exploration/common_voice/*.ipynb` | `experiments/pilot/notebooks/*.ipynb` |
| `data/exploration/common_voice/outputs/` | `experiments/pilot/notebooks/outputs/` |
| `scripts/train_aasist_pilot.py` / `experiments/pilot/scripts/train_aasist_clean.py` | `experiments/pilot/scripts/aasist/train_aasist_clean.py` |
| `scripts/check_aasist_overfit.py` / `experiments/pilot/scripts/check_aasist_overfit.py` | `experiments/pilot/scripts/aasist/check_aasist_overfit.py` |
| `src/thai_spoof/cvtts/pilot_data.py`, `overfit.py` | `src/thai_spoof/pilot/` |
| pilot-specific tests ใน `tests/cvtts/` | `tests/pilot/` |
| คู่มือ Clean/overfit ใน `docs/` / `experiments/pilot/docs/` | `experiments/pilot/docs/aasist/` |
| `results/cvtts/aasist_*/` | `results/pilot/aasist_*/` |

**ไม่ย้าย** raw audio, native/canonical pilot data หรือ pretrained weights เพื่อรักษา lineage/manifest paths ไม่มีการลบผลทดลองเก่า หรือแก้รายงานเก่าว่าเป็น run ใหม่

Historical run JSON ยังเก็บ code paths/hash ของตอนที่รันจริง หากย้อนตรวจ source ให้ใช้ Git เวอร์ชันก่อน refactor ไม่คาดหวังว่า source hash ปัจจุบันที่แก้ import/path จะตรงกับ run เก่า ดู [หมายเหตุการย้าย](../experiments/pilot/docs/PATH_MIGRATION_TH.md)

## งานจริงยังไม่มีอะไรบ้าง

ดู [Research README](../experiments/research/README.md) ตอนนี้ยังไม่มี multi-condition/main-run trainer, RawNet2 fine-tuning หรือ Final Test pipeline ใหม่ ห้ามใช้ CLI metrics เดิมแทน Dev-threshold protocol
