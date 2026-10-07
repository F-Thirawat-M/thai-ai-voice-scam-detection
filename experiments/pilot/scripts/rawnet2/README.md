# RawNet2 — พื้นที่สคริปต์ pilot ฝั่งเพื่อน

**ยังไม่มี trainer ในโฟลเดอร์นี้** README ทำให้เพื่อนเห็นที่สำหรับเพิ่มงาน ไม่ได้หมายความว่าฝึก RawNet2 ได้แล้ว

เมื่อพัฒนา trainer ให้เก็บที่นี่ เช่น `train_rawnet2_clean.py` (ชื่อเสนอ ยังไม่มีไฟล์) รันจาก project root และเขียนคู่มือไว้ `experiments/pilot/docs/rawnet2/` ไม่แก้สคริปต์ AASIST ให้กลายเป็น RawNet2

- Network/adapter/config: `src/thai_spoof/rawnet2/`
- โหลดข้อมูลร่วม: `src/thai_spoof/pilot/pilot_data.py`
- กฎ crop/repeat ร่วม: `src/thai_spoof/cvtts/windows.py`
- ข้อมูล: `data/processed/cvtts/pilot_v1/` ใช้ manifest Train/Dev เดียวกับ AASIST
- น้ำหนักเริ่มต้น: `checkpoints/rawnet2/pre_trained_DF_RawNet2.pth` ไม่ใช้ AASIST checkpoint
- ผลรอบใหม่: `results/pilot/rawnet2/<run_id>/` ต้องไม่เขียนทับรอบเดิม

อย่าคัดลอก dataset แยกตามโมเดล อย่าใช้ Dev เป็น Train และยังไม่มี Final Test ดู [คู่มือส่งต่องาน](../../../../docs/TEAM_HANDOFF_TH.md)
