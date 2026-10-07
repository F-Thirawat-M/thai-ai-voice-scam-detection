# แผนผังโปรเจกต์ — แยก pilot / research / โค้ดร่วม

## ให้ดูชื่อหมวดก่อน

- **pilot** = ทดลองให้ระบบทำงานและตรวจวิธีฝึก ยังไม่ใช่ผลวิจัยหลัก
- **research** = การทดลองจริงตาม protocol ที่จะล็อกภายหลัง ตอนนี้ยังไม่เริ่ม
- **src** = โค้ดที่ใช้ทำงาน ไม่ใช่ผลการทดลอง
- **data/results** = ข้อมูล/ผลในเครื่อง ไม่เข้า Git

```text
project/
├─ experiments/
│  ├─ pilot/                       ← งานที่เราทำอยู่ตอนนี้
│  │  ├─ README.md                 ← เปิดอันนี้ก่อน
│  │  ├─ notebooks/                ← EDA → TTS → เตรียมเสียง
│  │  │  └─ outputs/               ← notebook ที่รันแล้ว (ไม่เข้า Git)
│  │  ├─ scripts/                  ← Clean 1 epoch / จำ Train 4 คลิป
│  │  └─ docs/                     ← คำอธิบายและผลแต่ละขั้น
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
│  ├─ raw/common_voice/            ← เสียง/metadata ต้นทาง ห้ามแก้ in-place
│  ├─ processed/cvtts/pilot_v1/     ← เสียง/manifest pilot ไม่ใช่ corpus วิจัยหลัก
│  ├─ raw/noise/                   ← ยังไม่ได้เตรียม noise สำหรับการทดลองหลัก
│  └─ sample/                      ← เสียงลอง inference ไม่ใช่ชุด train/test
├─ results/
│  └─ pilot/
│     ├─ aasist_clean_smoke/       ← ผล Train 160 / Dev 40
│     └─ aasist_overfit_check/     ← ผลจำ Train 4 คลิป
├─ checkpoints/                   ← weights ของ detector/TTS ไม่ใช่ dataset
├─ external/aasist/               ← โครงข่ายต้นทางที่ยังใช้จริง
├─ scripts/                       ← setup/environment/smoke inference เท่านั้น
├─ configs/cvtts/                 ← dependencies ของ TTS pilot; ยังไม่มี main-run config
├─ docs/                          ← แผนภาพ/คู่มือภาพรวม/workflow/decisions
└─ tmp/                           ← ชั่วคราว; tmp/wayu-python เป็น base ของ .venv-wayu อย่าลบ
```

## ไฟล์ที่ใช้ตอนนี้

เปิด [Pilot README](../experiments/pilot/README.md) มีลำดับ notebook/คำสั่งและสถานะครบ ไม่ต้องไล่เปิดทุกไฟล์ใน src

Raw Common Voice และ pretrained ใช้ร่วมกันได้ ไม่แยกสำเนาตาม AASIST/RawNet2 ส่วนชุดข้อมูล/run สำหรับงานวิจัยจริงต้องสร้างเป็น version ใหม่ ไม่ตั้งชื่อ pilot_v1 เป็นงานจริงเฉย ๆ

## ย้ายอะไรบ้าง

| เดิม | ใหม่ |
| --- | --- |
| `data/exploration/common_voice/*.ipynb` | `experiments/pilot/notebooks/*.ipynb` |
| `data/exploration/common_voice/outputs/` | `experiments/pilot/notebooks/outputs/` |
| `scripts/train_aasist_pilot.py` | `experiments/pilot/scripts/train_aasist_clean.py` |
| `scripts/check_aasist_overfit.py` | `experiments/pilot/scripts/check_aasist_overfit.py` |
| `src/thai_spoof/cvtts/pilot_data.py`, `overfit.py` | `src/thai_spoof/pilot/` |
| pilot-specific tests ใน `tests/cvtts/` | `tests/pilot/` |
| คู่มือ Clean/overfit ใน `docs/` | `experiments/pilot/docs/` |
| `results/cvtts/aasist_*/` | `results/pilot/aasist_*/` |

**ไม่ย้าย** raw audio, native/canonical pilot data หรือ pretrained weights เพื่อรักษา lineage/manifest paths ไม่มีการลบผลทดลองเก่า หรือแก้รายงานเก่าว่าเป็น run ใหม่

Historical run JSON ยังเก็บ code paths/hash ของตอนที่รันจริง หากย้อนตรวจ source ให้ใช้ Git เวอร์ชันก่อน refactor ไม่คาดหวังว่า source hash ปัจจุบันที่แก้ import/path จะตรงกับ run เก่า ดู [หมายเหตุการย้าย](../experiments/pilot/docs/PATH_MIGRATION_TH.md)

## งานจริงยังไม่มีอะไรบ้าง

ดู [Research README](../experiments/research/README.md) ตอนนี้ยังไม่มี multi-condition/main-run trainer, RawNet2 fine-tuning หรือ Final Test pipeline ใหม่ ห้ามใช้ CLI metrics เดิมแทน Dev-threshold protocol
