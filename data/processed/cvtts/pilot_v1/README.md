# pilot_v1 — ข้อมูลร่วม AASIST / RawNet2

**ชุดทดลองเล็ก ไม่ใช่ corpus งานวิจัยหลัก** Git มีเพียงคู่มือและ `.gitkeep` เสียง/CSV/JSON ต้องเตรียมหรือรับ ZIP แยก

| โฟลเดอร์ | หน้าที่ |
| --- | --- |
| `canonical/clean16k/train/bonafide/` | WAV เสียงคนสำหรับ Train 80 คลิป |
| `canonical/clean16k/train/spoof/` | WAV Wayu สำหรับ Train 80 คลิป |
| `canonical/clean16k/dev/bonafide/`, `dev/spoof/` | Dev อย่างละ 20 คลิป |
| `native_tts/wayu/train/`, `wayu/dev/` | เสียงสร้างจาก Wayu ที่ sample rate เดิม |
| `native_tts/mms_tha/train/` | ผลลอง MMS เดิม ไม่ใช่ spoof หลักของ canonical pilot นี้ |
| `manifests/` | CSV รายการข้อมูล/label/เส้นทาง/hash ไม่ใช่ตัวเสียง |
| `qc/` | รายงานการสร้าง/เตรียมเสียง ไม่ใช่คะแนน detector |

ตัวฝึกอ่าน `manifests/wayu_pilot_train_clean16k.csv` (160 แถว) และ `manifests/wayu_pilot_dev_clean16k.csv` (40 แถว) ตาม canonical report ใน `qc/canonical_audio/` Loader ตรวจ original MP3 และ native TTS ด้วย จึงไม่ควรส่งเฉพาะ canonical WAV

WAV mono 16 kHz ความยาวเต็ม กฎ window ใช้ตอนป้อนโมเดล ไม่แก้ WAV ชุดนี้ยังไม่มี Final Test ไม่แยกสำเนาตามโมเดล ดู [คู่มือส่งต่อ](../../../../docs/TEAM_HANDOFF_TH.md)
