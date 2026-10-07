# Pilot notebooks — ดูลำดับ ไม่ต้องเปิดพร้อมกันทุกไฟล์

| ลำดับ | Notebook | Kernel | ทำอะไร |
| --- | --- | --- | --- |
| 1 | [common_voice_eda](common_voice_eda.ipynb) | `.venv` | ดู df/คอลัมน์/เสียง แล้วสร้าง Train 80 / Dev 20 |
| 2 | [common_voice_tts_pilot](common_voice_tts_pilot.ipynb) | `.venv` | ลอง MMS; เป็นขั้นทดลองเก่า ไม่ได้ฝึก detector |
| 3 | [common_voice_wayu_tts_pilot](common_voice_wayu_tts_pilot.ipynb) | `.venv-wayu` | ลอง/ฟัง Wayu 10 คลิป |
| 4 | [common_voice_wayu_pilot_dataset](common_voice_wayu_pilot_dataset.ipynb) | `.venv-wayu` | สร้าง Wayu Train 80 / Dev 20 |
| 5 | [common_voice_pilot_audio](common_voice_pilot_audio.ipynb) | `.venv` | เตรียมคน+Wayu เป็น WAV mono 16 kHz ความยาวเต็ม |

สำเนาที่รันแล้วอยู่ `outputs/` มีชื่อเหมือนเดิมต่อด้วย `.executed.ipynb` ไม่เข้า Git เปิดดูผลได้โดยไม่รันใหม่

ทุก notebook หา project root ผ่าน `pyproject.toml` ไม่ขึ้นกับตำแหน่งโฟลเดอร์เดิม และยังใช้ dataset/weights เดิม ไม่ย้ายเสียง

Notebook ไม่ใช่การ fine-tune detector ขั้นฝึกอยู่ [../scripts/](../README.md) ดู [หน้าเริ่ม pilot](../README.md) สำหรับสถานะปัจจุบัน หรือ [รายละเอียด notebook](../docs/NOTEBOOK_DETAILS_TH.md) เมื่อจำเป็น
