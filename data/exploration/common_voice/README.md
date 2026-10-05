# Common Voice EDA แบบง่าย

เปิด [common_voice_eda.ipynb](common_voice_eda.ipynb) ใน VS Code เลือก **Select Kernel → Python Environments → .venv** แล้วกด **Run All** หรือรันทีละเซลล์จากบนลงล่าง เริ่มด้วย `pd.read_csv()`, `df.head()`, `df.shape`, `df.info()` และ `df.columns`

สิ่งที่ดูได้: ไฟล์ TSV ทั้งแพ็กและบทบาท, จำนวนคลิป, 13 คอลัมน์ต้นทาง, ค่าว่าง, ชื่อไฟล์/ข้อความซ้ำ, ความยาวเสียงและคลิปที่เกิน 4.04/6/8 วินาที, อายุ/เพศ/สำเนียง, speaker keys, โหวต, ข้อความ, ไฟล์เสียงที่มีจริง และ sample rate/channels ของตัวอย่าง 5 คลิป พร้อมฟังตัวอย่างหนึ่งคลิป

ใช้ pandas ตรงใน notebook ไม่ต้องเรียก helper หรือ CLI ใหม่ ข้อมูลดิบที่ใช้คือ `data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/` ส่วนผลที่รันแล้วอยู่ [outputs/common_voice_eda.executed.ipynb](outputs/common_voice_eda.executed.ipynb) ในเครื่องนี้และไม่เข้า Git

`df` คือ validated; `df_all` รวม validated/invalidated/other เท่านั้น Train/Dev/Test ต้นทางเป็นส่วนย่อยจึงไม่บวกซ้ำ คอลัมน์ `clip_status`/`duration_s` เป็นสิ่งที่เติมเองเพื่อดูข้อมูล ไม่ใช่ฟีเจอร์ต้นทางหรือ input โมเดล

ความยาวทั้งหมดอ่านจาก metadata ไม่ใช่ decode ทุกไฟล์; จำนวน client_id คือรหัสผู้พูดไม่ซ้ำในต้นทาง ยังไม่ยืนยันจำนวนบุคคลจริง Notebook ไม่แก้ raw data ไม่สร้าง TTS ไม่แบ่งชุดใหม่ และไม่ train

ก่อน commit notebook ต้นแบบให้ clear outputs; เก็บไฟล์ที่มีผลจริงใน `outputs/` แผนงานฉบับละเอียดอยู่ใน [workflow Phase 1](../../../docs/COMMON_VOICE_PROJECT_WORKFLOW_TH.md#s08)
