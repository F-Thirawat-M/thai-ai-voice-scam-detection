# Data — เก็บข้อมูล ไม่ใช่ notebook/คำสั่งฝึก

| ที่อยู่ | ความหมาย |
| --- | --- |
| `raw/common_voice/cv-corpus-27.0-2026-09-11/th/` | Common Voice ต้นทาง ไม่แก้ in-place |
| `processed/cvtts/pilot_v1/` | **ชุดทดลองเล็กเท่านั้น** ไม่ใช่ corpus งานวิจัยจริง |
| `processed/cvtts/pilot_v1/native_tts/` | MMS/Wayu ที่ sample rate เดิม |
| `processed/cvtts/pilot_v1/canonical/clean16k/` | คน+Wayu WAV mono 16 kHz เต็มคลิป |
| `processed/cvtts/pilot_v1/manifests/` | รายการข้อมูล pilot และ hashes |
| `processed/cvtts/pilot_v1/qc/` | รายงานการเตรียมข้อมูล/สร้างเสียง ไม่ใช่คะแนน detector |
| `raw/noise/` | พื้นที่ noise ที่ยังไม่เตรียมสำหรับงานหลัก |
| `sample/` | เสียงลอง inference ไม่ใช่ Train/Dev/Test |

**Notebook ย้ายไป [experiments/pilot/notebooks/](../experiments/pilot/notebooks/README.md)** ไม่อยู่ใน data/exploration แล้ว ผลฝึกอยู่ [results/pilot/](../results/pilot/) ไม่ใช่ qc ของ dataset

Raw/processed/sample เสียงจริงไม่เข้า Git ส่วน root รายงานที่ commit ได้อยู่ใน docs ไม่มีการทำสำเนา raw data แยกตามโมเดล และยังไม่ได้สร้าง dataset version สำหรับการทดลองจริง
