# ผลตรวจ seeds 42 / 43 / 44 — pilot เท่านั้น

`<suite_id>/` มี `run.json`, `summary.json`, `seed_curves.png` ไฟล์จริงไม่อยู่ใน Git คู่มือนี้บอกตำแหน่งเท่านั้น

ใช้ seed 42 เดิมที่ตรวจผ่าน และฝึกใหม่เฉพาะ 43/44 อย่างละ 3 epochs ภายใต้ `results/pilot/aasist_frozen_bn_curve/<suite_id>_seed43/`, `<suite_id>_seed44/` รายงานทั้งสาม ไม่เลือก seed ที่ดีที่สุด ดู [คู่มือ](../../../experiments/pilot/docs/aasist/AASIST_SEED_STABILITY_TH.md)
