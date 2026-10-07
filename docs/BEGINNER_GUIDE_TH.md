# เริ่มทำงานต่อ — สำหรับผู้เริ่มต้น

**ตอนนี้อยู่ใน pilot** ให้เปิด [experiments/pilot/README.md](../experiments/pilot/README.md) เป็นหน้าแรก มีขั้นตอนเรียงไว้แล้ว ไม่ต้องรันใหม่ทุกขั้น

- AASIST/RawNet2 คือโมเดลตรวจเสียง ไม่ใช่ TTS
- Wayu/MMS คือ TTS สร้างเสียงปลอมจากข้อความ ไม่ได้ train TTS เองใน pilot
- Inference คือทำนายด้วย weights ที่มี; fine-tuning คือฝึกปรับ weights เพิ่ม
- Epoch คือผ่านข้อมูล Train หนึ่งรอบ; optimizer update คือหนึ่งครั้งที่ปรับ weights ไม่ใช่จำนวนคลิป
- Train ใช้ฝึก; Dev ใช้เลือกวิธี/ตรวจผล; Final Test ใช้ประเมินขั้นสุดท้าย ไม่เอาคะแนนกลับมาจูน
- Clean คือไม่เติม noise/telephone จำลอง ไม่รับประกันว่าเสียงต้นทางไม่มี noise

## เลือก Python ให้ถูก

- `.venv` หลัก: EDA, MMS, canonical audio, AASIST, tests
- `.venv-wayu`: notebook สร้างเสียง Wayu เท่านั้น

ไฟล์ WAV เต็มเก็บไว้เหมือนเดิม การใช้ 64,600 samples (ประมาณ 4.04 วินาที) เกิดตอนสร้าง tensor เข้าโมเดล ไม่ใช่ข้อจำกัดความยาวไฟล์ที่รับได้

## ตรวจเครื่อง

รันจาก project root:

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe -m pytest -q
```

setup มีการดาวน์โหลด/ติดตั้ง ไม่รันซ้ำโดยไม่จำเป็น ส่วน `tmp/wayu-python` เป็น Python base ของ Wayu environment ไม่ใช่โฟลเดอร์ที่ลบได้ตามชื่อ tmp

## ดูงานจริง

[Research README](../experiments/research/README.md) บอกอะไรยังเป็นแผน ส่วน [Workflow ยาว](COMMON_VOICE_PROJECT_WORKFLOW_TH.md) เป็นเอกสารออกแบบ ไม่ได้หมายความว่าทุกคำสั่งมีแล้ว
