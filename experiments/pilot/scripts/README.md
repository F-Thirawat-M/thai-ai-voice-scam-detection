# Pilot scripts — ไม่ใช่การทดลองวิจัยจริง

- [aasist/](aasist/README.md): ฝั่ง AASIST มี Clean 1 epoch / short preflight และจำ Train 4 คลิป
- [rawnet2/](rawnet2/README.md): ฝั่งเพื่อนที่จะเพิ่ม RawNet2 trainer ตอนนี้ยังไม่มีโค้ดฝึก

Dataset/label/window ที่ใช้ร่วมกันอยู่ `src/thai_spoof/pilot/` และ `src/thai_spoof/cvtts/` ไม่คัดลอก loader ไปไว้ในแต่ละโมเดล Notebook EDA/TTS/audio preparation อยู่ `../notebooks/` และใช้ร่วมกัน

รันจาก project root ไม่จำเป็นต้อง cd เข้ามา ใช้ `.venv` หลัก ผลอยู่ `results/pilot/` แต่ละ run ต้องชื่อใหม่ ไม่ overwrite ผลเดิม

ดูคำสั่ง/ผลที่ [Pilot README](../README.md) ยังไม่มี RawNet2 trainer หรือ main-run trainer ที่นี่
