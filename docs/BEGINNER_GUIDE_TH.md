# คู่มือสำหรับผู้เริ่มต้น

## โมเดลกำลังทำอะไร

AASIST รับคลื่นเสียงประมาณ 4 วินาทีและคืนคะแนนสองค่า:

- `spoof`: โมเดลพบลักษณะคล้ายเสียงสังเคราะห์
- `bonafide`: โมเดลพบลักษณะคล้ายเสียงมนุษย์จริง

โมเดลที่มากับ repository ฝึกจาก ASVspoof 2019 ซึ่งไม่ใช่ชุดข้อมูลภาษาไทย ผลแรกจึงเรียกว่า **cross-language baseline** ไม่ใช่ผลสุดท้ายของโครงงาน

## คำศัพท์สำคัญ

- **Inference**: ใช้โมเดลที่ฝึกแล้วทำนายไฟล์ใหม่
- **Training**: ปรับพารามิเตอร์โมเดลด้วยข้อมูลที่มี label
- **Fine-tuning**: นำโมเดลเดิมมาฝึกเพิ่มด้วยข้อมูลของเรา
- **Checkpoint**: ไฟล์พารามิเตอร์ที่โมเดลเรียนรู้แล้ว
- **Bonafide**: เสียงจริง
- **Spoof**: เสียงปลอมหรือเสียงสังเคราะห์
- **EER**: จุดที่อัตรารับเสียงปลอมผิดและปฏิเสธเสียงจริงผิดเท่ากัน ค่ายิ่งต่ำยิ่งดี
- **SNR**: อัตราส่วนสัญญาณเสียงพูดต่อเสียงรบกวน ค่ายิ่งต่ำยิ่งมี noise มาก

## Milestone 1: ระบบรันได้

สิ่งที่ถือว่าผ่าน:

1. `scripts/check_environment.py` เห็น CUDA และ RTX 3050 Ti
2. คำสั่ง `infer` โหลด checkpoint สำเร็จ
3. โปรแกรมอ่าน WAV หนึ่งไฟล์และแสดง prediction ได้

ผลการทำนายในช่วงนี้อาจผิดได้ เพราะยังไม่ได้ปรับโมเดลให้เข้ากับภาษาไทย

## Milestone 2: Thai clean baseline

เมื่อได้ SEA-Spoof:

1. เลือกเฉพาะ `language=th`
2. ตรวจ official train/validation/evaluation split
3. ตรวจไม่ให้ผู้พูดซ้ำข้าม split
4. สร้าง CSV manifest
5. รัน `evaluate`
6. เก็บ EER, ROC-AUC, accuracy และ confusion matrix

## Milestone 3: Telephone robustness

สร้างสำเนาเสียงทดสอบในเงื่อนไขต่อไปนี้:

- Clean
- narrow-band/telephone codec
- Noise ที่ 20, 10 และ 0 dB
- telephone codec ร่วมกับ noise

ห้ามใช้ไฟล์ evaluation ไปฝึกโมเดล และต้องใช้ไฟล์ต้นฉบับชุดเดียวกันทุกเงื่อนไขเพื่อให้เปรียบเทียบอย่างยุติธรรม

## Milestone 4: Fine-tuning

RTX 3050 Ti มี VRAM 4 GB จึงเริ่มด้วย batch size 2 และ mixed precision หลังจาก baseline ถูกต้องแล้วเท่านั้น การฝึกเต็มชุดอาจต้องใช้ cloud GPU

## สิ่งที่ยังไม่ควรทำ

- อย่าเริ่มจากสร้างเว็บหรือ mobile application
- อย่าแก้ architecture ก่อนมี baseline
- อย่าสุ่มแบ่งไฟล์โดยไม่ดู speaker และ TTS system
- อย่าสรุปว่า softmax 0.9 หมายถึงโมเดลถูก 90%
- อย่ารายงานผลจากไฟล์ตัวอย่างไม่กี่ไฟล์เป็นผลวิจัย

