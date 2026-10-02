# สำรวจข้อมูล

เก็บ notebook/helper เฉพาะการสำรวจแยกตาม dataset ปัจจุบันเตรียมเฉพาะ [Common Voice](common_voice/README.md) สำหรับแผนใหม่ ยังไม่มี notebook หรือผลสำรวจ Common Voice ที่สร้างจากโครงสร้างนี้

```text
data/exploration/common_voice/
  README.md
  common_voice_eda.ipynb    # จะสร้างใน task T02
  outputs/                 # ตารางและ notebook ที่มีข้อมูลจริง ไม่ commit
```

เสียงต้นทางอยู่ `data/raw/common_voice/<release>/`; manifest ที่ใช้ทำซ้ำการทดลองอยู่ `data/processed/cvtts/<version>/manifests/` ไม่วาง dataset ขนาดใหญ่ไว้ข้าง notebook และไม่คัดลอกชุดข้อมูลแยกตาม AASIST/RawNet2

Notebook ควรเรียก helper จาก `src/thai_spoof/cvtts/` แทนคัดลอก logic หลายแห่ง ก่อน commit ให้ล้าง outputs ที่มีข้อมูลส่วนตัวหรือเนื้อหาที่แจกไม่ได้

EDA ของ SEA-Spoof/Typhoon และผลเดิมถูกลบแล้วตามคำขอ เป้าหมายใหม่ดู [workflow](../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md)
