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

เครื่องนี้ดาวน์โหลดและแตก Common Voice Thai 27.0 ไว้แล้วที่ `raw/common_voice/cv-corpus-27.0-2026-09-11/th/` มี notebook EDA, MMS/Wayu review10, [Wayu ครบ pilot Train/Dev](exploration/common_voice/common_voice_wayu_pilot_dataset.ipynb) และ [shared canonical audio](exploration/common_voice/common_voice_pilot_audio.ipynb) มี [AASIST Clean 1-epoch smoke](../docs/AASIST_CLEAN_SMOKE_TH.md) แล้ว แต่ยังไม่ได้เตรียม noise หรือ fine-tune รอบวิจัยเต็ม ผล smoke อยู่ `results/cvtts/aasist_clean_smoke/` ไม่แก้ dataset หากข้อมูลอยู่ที่อื่นต้องเพิ่ม config/data-root support ก่อนใช้ script smoke ไม่ย้าย/ทำสำเนาก้อนใหญ่โดยไม่จำเป็น

ไม่ใช้ `data/manifests/` กลางอีกแล้ว เพราะ manifest ต้องผูกกับ dataset version; ตัวอย่างที่แจกได้ย้ายไป `examples/` ส่วน config ไม่เก็บ tokens

ขั้นเตรียมทดลองใน notebook Common Voice บันทึกชุดเล็กที่ `processed/cvtts/pilot_v1/` เป็นรายการเสียงจริง Train 80 / Dev 20 และรายงานตรวจ split โดยอ้างถึง MP3 ดิบ ไม่คัดลอกเสียง ในขั้นแบ่งข้อมูลยังไม่มี TTS และยังไม่มี Final Test; ใช้ลองกระบวนการ ไม่ใช่ชุดสำหรับสรุปผลวิจัย

ขั้น TTS feasibility แยกเป็น `exploration/common_voice/common_voice_tts_pilot.ipynb` สร้าง MMS Thai จากข้อความ Train เพียง 1 คลิปไว้ใน `processed/cvtts/pilot_v1/native_tts/` พร้อม provenance และสถานะรอฟังตรวจ ไม่ใช่การสร้างทั้ง dataset หรือการ fine-tune ตัวตรวจจับ

หัวข้อ TTS review batch ขยายตัวอย่าง Train เป็น 10 คลิป (รวมคลิปแรก) เพื่อฟังข้อความสั้นถึงยาว รายการอยู่ `manifests/tts_train_review10.csv` ภายใน pilot version และผลฟังตรวจอยู่ `qc/tts_reviews/` ไม่ใช่ชุด train ที่พร้อมใช้ทั้งสองคลาสและไม่มี TTS จาก Dev ในขั้นนี้

ขั้น Wayu ครบ pilot ใช้เสียงเดิมที่ตรวจแล้ว และสร้างเพิ่มให้เป็น Train 80 / Dev 20 เก็บใน `native_tts/wayu/<split>/` พร้อม `tts_wayu_train.csv`, `tts_wayu_dev.csv`, `tts_wayu_all.csv` และรายการสองคลาส `wayu_pilot_train_native.csv` / `wayu_pilot_dev_native.csv` มีคนจริง/ปลอมอย่างละ 80 ใน Train และอย่างละ 20 ใน Dev รายการ native ยังต่าง codec/sample rate จึงต้องเตรียมรูปแบบเสียงร่วมก่อน train ไม่มี Final Test ไม่เติม noise/telephone ไม่ train และไม่ใช่การตัด TTS ตัวอื่นออกจากแผนวิจัย รายละเอียดใน [README notebook](exploration/common_voice/README.md)

ขั้น shared canonical audio เตรียมไฟล์ใหม่ที่ `canonical/clean16k/<split>/<label>/` ทั้งสองคลาสเป็น WAV FLOAT mono 16 kHz รวม 200 คลิป พร้อม `wayu_pilot_train_clean16k.csv` (160) / `wayu_pilot_dev_clean16k.csv` (40) และ source/output hashes เก็บความยาวเต็ม ไม่ normalize gain/crop/pad/เติม noise ไม่แก้ native data ไม่ใช่การรับประกันว่าต้นทางทั้งสองคลาสมี bandwidth/คุณภาพเท่ากัน และยังต้องเพิ่ม training DataLoader/window/trainer ก่อนลองฝึก

กติกา split, QC และฟิลด์ทั้งหมดอยู่ใน [workflow](../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md) อย่าถือว่า `.gitignore` เพียงอย่างเดียวตรวจสิทธิ์การแชร์ข้อมูลให้แล้ว
