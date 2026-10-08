# AASIST — สคริปต์ pilot ฝั่งผู้ทำ AASIST

- [train_aasist_clean.py](train_aasist_clean.py): Clean 1 epoch, Train 160 / Dev 40 หรือ preflight สั้น
- [check_aasist_overfit.py](check_aasist_overfit.py): จำ Train 4 คลิป ไม่โหลด Dev/Test
- [check_aasist_batchnorm.py](check_aasist_batchnorm.py): เทียบสองรอบ Clean เปลี่ยนเฉพาะโหมด BN, Train 160 / Dev 40 ไม่โหลด Test
- [train_aasist_frozen_bn.py](train_aasist_frozen_bn.py): Frozen BN แบบกำหนด 3 epochs, Train/Dev curve และ checkpoint ทุก epoch ไม่โหลด Test
- [check_aasist_seed_stability.py](check_aasist_seed_stability.py): อ่าน reference seed 42 แล้วฝึก 43/44 อย่างละ 3 epochs สรุปทั้งสาม ไม่เลือก seed ที่ดีที่สุด

รันจาก project root ด้วย `.venv` หลัก ใช้ run-id ใหม่ทุกครั้ง ไม่ใช่การทดลองวิจัยหลัก ดู [คู่มือ AASIST](../../docs/aasist/README.md) สำหรับคำสั่งและข้อจำกัด

โครงข่าย/adapter อยู่ `src/thai_spoof/aasist/` ข้อมูลอ่านผ่าน shared loader `src/thai_spoof/pilot/pilot_data.py` ไม่ใช่ loader แยกของ AASIST
