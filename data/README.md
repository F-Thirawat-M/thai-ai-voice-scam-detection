# การจัดการข้อมูลสำหรับ Common Voice + TTS

ใช้ dataset ชุดเดียวร่วมกันระหว่าง AASIST/RawNet2 แยกผลตาม model ไม่แยกสำเนาข้อมูลตาม model

| ตำแหน่ง | หน้าที่ | เข้า Git |
| --- | --- | --- |
| `raw/common_voice/<release>/` | archive/metadata/audio ต้นทางที่ได้รับสิทธิ์; ไม่แก้ in-place | ไม่เข้า |
| `raw/noise/<source>/` | noise recordings ต้นทางพร้อมสิทธิ์และ split mapping | ไม่เข้า |
| `processed/cvtts/<version>/native_tts/` | เสียง TTS native sample rate | ไม่เข้า |
| `processed/cvtts/<version>/canonical/` | เสียงเต็มที่ผ่าน preprocessing กลาง | ไม่เข้า |
| `processed/cvtts/<version>/manifests/` | source/split/base/condition manifests ของ dataset version | ไม่เข้า |
| `processed/cvtts/<version>/conditions/` | cache Dev/Test condition ที่คงที่ | ไม่เข้า |
| `processed/cvtts/<version>/qc/`, `jobs/`, `locks/` | QC, resume ledger, provenance/hash | ไม่เข้า |
| `exploration/common_voice/` | notebook และคู่มือสำรวจที่ล้างข้อมูลอ่อนไหวแล้ว | เข้า |
| `exploration/common_voice/outputs/` | ตารางรายละเอียด ผล EDA และ executed notebook | ไม่เข้า |
| `sample/` | เสียงทดลองส่วนตัว ไม่ใช่ corpus วิจัย | เฉพาะ README เข้า |

เครื่องนี้ดาวน์โหลดและแตก Common Voice Thai 27.0 ไว้แล้วที่ `raw/common_voice/cv-corpus-27.0-2026-09-11/th/` และมี notebook EDA แบบง่าย ยังไม่ได้เตรียม noise หรือสร้าง TTS ใหม่ หากข้อมูลอยู่ที่อื่นให้ระบุ data root ใน config ไม่ย้าย/ทำสำเนาก้อนใหญ่โดยไม่จำเป็น

ไม่ใช้ `data/manifests/` กลางอีกแล้ว เพราะ manifest ต้องผูกกับ dataset version; ตัวอย่างที่แจกได้ย้ายไป `examples/` ส่วน config ไม่เก็บ tokens

กติกา split, QC และฟิลด์ทั้งหมดอยู่ใน [workflow](../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md) อย่าถือว่า `.gitignore` เพียงอย่างเดียวตรวจสิทธิ์การแชร์ข้อมูลให้แล้ว
