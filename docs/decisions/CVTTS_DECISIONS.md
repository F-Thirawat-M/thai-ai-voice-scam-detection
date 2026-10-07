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
- Branch `feat-aasist-clean-smoke` แยกจาก canonical audio ที่ผู้ใช้ commit แล้ว; ผู้ใช้ commit/push เอง รายละเอียดและคำสั่งอยู่ [คู่มือ](../AASIST_CLEAN_SMOKE_TH.md)

## ยังรอยืนยันก่อนล็อก protocol

- Common Voice exact release/root/สิทธิ์
- fixed experiment หรือ adaptive Dev loop; TTS-only หรือจำเป็นต้อง cloning
- ขอบเขต demographic analysis และ held-out generator
- generators/revisions, cohort size, noise pool, telephone profile, tuning/compute budget

ค่าตัวเลขใน workflow เป็นข้อเสนอสำหรับ pilot ไม่ใช่ผลหรือข้อตกลงที่อาจารย์อนุมัติแล้ว เมื่อมีคำตอบให้เพิ่มวันที่ ผู้ยืนยัน เหตุผล และผลกระทบต่อ protocol version
