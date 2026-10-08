# คู่มือ AASIST pilot

- [Clean 1 epoch](AASIST_CLEAN_SMOKE_TH.md): Train 160 / Dev 40 ฝึก/reload ได้ แต่ Dev loss แย่ลง
- [จำ Train 4 คลิป](AASIST_OVERFIT_CHECK_TH.md): ผ่านการตรวจการเรียนรู้บนคลิปที่ฝึกซ้ำ ไม่ใช่ accuracy ของเสียงใหม่
- [ตรวจโหมด BatchNorm](AASIST_BATCHNORM_CHECK_TH.md): controlled pair จาก pretrained เดิม เปลี่ยนเฉพาะโหมด BN ไม่ใช่ Final Test
- [Frozen BN 3 epochs](AASIST_FROZEN_BN_CURVE_TH.md): งบเล็กที่กำหนดก่อนรัน ดู Train/Dev curve และเลือก trained checkpoint ด้วย Dev
- [ตรวจ seeds 42/43/44](AASIST_SEED_STABILITY_TH.md): ตรวจ recipe/data/source compatibility และสรุปทุก seed พร้อมค่าเฉลี่ย/ความแกว่ง ไม่ใช่ Test

สคริปต์อยู่ [scripts/aasist/](../../scripts/aasist/README.md) ผลจริงในเครื่องอยู่ `results/pilot/aasist_clean_smoke/` และ `results/pilot/aasist_overfit_check/` ไม่อยู่ใน Git
