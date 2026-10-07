# Shared helpers — ไม่ใช่ main-run trainer

โค้ดกลางที่ใช้ใน pilot และนำไปพัฒนางานวิจัยต่อได้:

| ไฟล์ | หน้าที่ |
| --- | --- |
| `audio.py` | full-clip mono/resample/WAV FLOAT ไม่มี crop หรือ gain normalization |
| `windows.py` | random-inclusive / first crop / short repeat |
| `artifacts.py` | เขียน derived artifacts แบบไม่ทับไฟล์เดิม |
| `provenance.py` | code hash guard รองรับเฉพาะ LF/CRLF difference |
| `text.py` | text validation สำหรับ MMS Thai pilot |

Dataset และการทดลองจำชุดเล็กย้ายไป `../pilot/` แล้ว ไม่อยู่รวมกับ helpers ที่ใช้ร่วมกัน

หน้าเริ่มงานอยู่ [Pilot README](../../../experiments/pilot/README.md) ยังไม่มี multi-condition/main-run/Dev-threshold/Final Test trainer ครบตาม [workflow](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md)
