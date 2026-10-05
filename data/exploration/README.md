# สำรวจข้อมูล

เก็บ notebook เฉพาะการสำรวจแยกตาม dataset ปัจจุบันมี [Common Voice EDA แบบง่าย](common_voice/common_voice_eda.ipynb) ที่ใช้ pandas ตรง ๆ และ [คู่มือเปิดใช้งาน](common_voice/README.md)

```text
data/exploration/common_voice/
  README.md
  common_voice_eda.ipynb    # EDA แบบง่าย; ต้นแบบไม่มี outputs
  outputs/                 # ตารางและ notebook ที่มีข้อมูลจริง ไม่ commit
```

เสียงต้นทางอยู่ `data/raw/common_voice/<release>/`; manifest ที่ใช้ทำซ้ำการทดลองอยู่ `data/processed/cvtts/<version>/manifests/` ไม่วาง dataset ขนาดใหญ่ไว้ข้าง notebook และไม่คัดลอกชุดข้อมูลแยกตาม AASIST/RawNet2

Notebook แบบเบื้องต้นใช้ pandas ตรงเพื่อให้อ่านง่าย หากภายหลังพัฒนา audit/split ที่ใช้ซ้ำใน pipeline จึงย้าย logic ไป helper กลางใน `src/thai_spoof/cvtts/` ก่อน commit ให้ล้าง outputs ที่มีข้อมูลส่วนตัวหรือเนื้อหาที่แจกไม่ได้

EDA ของ SEA-Spoof/Typhoon และผลเดิมถูกลบแล้วตามคำขอ เป้าหมายใหม่ดู [workflow](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md)
