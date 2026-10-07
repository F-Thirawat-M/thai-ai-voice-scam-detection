# คู่มือ RawNet2 pilot — ยังไม่มีการฝึก

พื้นที่สำหรับเพื่อนบันทึก recipe/คำสั่ง/ผล/ข้อจำกัดเมื่อเพิ่ม trainer ใน [scripts/rawnet2/](../../scripts/rawnet2/README.md)

ตอนนี้มี network/adapter และการเตรียม pretrained ใน `src/thai_spoof/rawnet2/` แต่ยังไม่มี RawNet2 fine-tuning pilot ห้ามนำผล AASIST มารายงานเป็นผล RawNet2

ใช้ Train 160 / Dev 40 และ canonical audio ชุดเดียวกัน รักษา label mapping/window policy ที่ตกลงไว้ พร้อมบันทึก hash/seed/weights/config/device/run-id และตรวจ reload ก่อนเปรียบเทียบกับ AASIST ดู [คู่มือส่งต่องาน](../../../../docs/TEAM_HANDOFF_TH.md)
