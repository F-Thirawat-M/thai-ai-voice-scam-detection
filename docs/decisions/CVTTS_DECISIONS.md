# Decision log

## 3 ตุลาคม 2026 — ปรับขอบเขตและจัด repository

- ตามความเข้าใจล่าสุด ใช้ Common Voice Thai + TTS เป็นแกนหลัก เปรียบเทียบ AASIST/RawNet2 แบบ Clean และ Mixed
- ผู้ใช้อนุญาตให้ลบข้อมูล/โค้ด/เอกสารที่ไม่ใช้แล้ว จึงนำ SEA-Spoof/Typhoon pipelines และ local datasets เก่าออก ไม่เก็บ archive ซ้ำใน project
- คง package และ pretrained weights ของสอง detector เพราะยังใช้ต่อ ไม่ย้ายเส้นทาง model เพียงเพื่อเปลี่ยนชื่อโฟลเดอร์
- Manifest จริงอยู่ใต้ `data/processed/cvtts/<version>/manifests/`; ตัวอย่างที่แจกได้อยู่ `examples/`
- ยังไม่มีการดาวน์โหลดข้อมูลใหม่ สร้าง TTS หรือ fine-tune ในการปรับโครงสร้างครั้งนี้
- ผู้ใช้ commit เอง; branch ของงานนี้คือ `refactor-common-voice-layout`

## ยังรอยืนยันก่อนล็อก protocol

- Common Voice exact release/root/สิทธิ์
- fixed experiment หรือ adaptive Dev loop; TTS-only หรือจำเป็นต้อง cloning
- ขอบเขต demographic analysis และ held-out generator
- generators/revisions, cohort size, noise pool, telephone profile, tuning/compute budget

ค่าตัวเลขใน workflow เป็นข้อเสนอสำหรับ pilot ไม่ใช่ผลหรือข้อตกลงที่อาจารย์อนุมัติแล้ว เมื่อมีคำตอบให้เพิ่มวันที่ ผู้ยืนยัน เหตุผล และผลกระทบต่อ protocol version
