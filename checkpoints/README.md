# น้ำหนักโมเดล (ไม่อยู่ใน Git)

- [aasist/](aasist/README.md): pretrained AASIST สำหรับตรวจ/fine-tune
- [rawnet2/](rawnet2/README.md): pretrained RawNet2 ของฝั่งเพื่อน
- [tts/](tts/README.md): โมเดลสร้างเสียง MMS/Wayu ไม่ใช่ detector

Git เก็บเฉพาะคู่มือและไฟล์ว่างบอกตำแหน่ง ไม่เก็บ `.pth`, `.pt`, `.safetensors`, config/tokenizer/voice assets ที่ดาวน์โหลดมา ผล fine-tune เป็น checkpoint ของแต่ละ run ใน `results/` ไม่ทับ pretrained ที่นี่
