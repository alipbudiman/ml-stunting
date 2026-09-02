# ML Stunting API

Layanan ini menyediakan API berbasis FastAPI untuk mendukung deteksi kondisi pertumbuhan anak menggunakan model machine learning dan perhitungan Z-score, serta integrasi data dari perangkat IoT.

## Gambaran Umum Sistem

Proyek ini dirancang sebagai fondasi layanan prediksi stunting yang dapat digunakan oleh aplikasi pendamping (dashboard, aplikasi mobile, atau sistem monitoring). API menerima data antropometri anak, mengolahnya menjadi indikator pertumbuhan, lalu mengembalikan hasil klasifikasi status gizi dan rekomendasi pesan tindak lanjut.

Selain prediksi, sistem juga mendukung:
- penerimaan data berat/tinggi dari perangkat IoT,
- pemantauan data perangkat secara real-time melalui WebSocket,
- pengelolaan status perangkat (trigger dan reset),
- endpoint kesehatan layanan untuk observabilitas.

## Nilai Penggunaan

Dengan struktur ini, tim pengembang dapat:
- mengintegrasikan proses skrining stunting ke alur digital secara konsisten,
- memisahkan komponen akuisisi data (IoT) dan komponen analitik (API),
- mempercepat validasi prototipe sebelum masuk ke deployment produksi.

## Fitur Utama

- Prediksi status pertumbuhan anak melalui endpoint `/predict`
- Perhitungan Z-score (BB/U, TB/U, BB/TB) sebagai dasar analitik
- Penerimaan data perangkat IoT melalui endpoint `/recive`
- Distribusi data perangkat secara periodik via WebSocket `/ws/data/{device_id}`
- Endpoint pemantauan perangkat: `/ws/status`, `/devices`, `/devices/{device_id}`
- Endpoint kontrol perangkat: `/trigger/{did}`, `/reset/{did}`
- Dokumentasi API otomatis melalui Swagger dan ReDoc

## Arsitektur Alur Kerja Singkat

1. Perangkat atau klien mengirim data tinggi/berat ke endpoint penerimaan data.
2. Data disimpan sementara pada memori aplikasi sebagai status perangkat aktif.
3. Klien dashboard dapat menarik data terbaru melalui WebSocket berdasarkan `device_id`.
4. Saat data anak lengkap tersedia, klien mengirimkan permintaan prediksi.
5. Sistem menghitung Z-score, menjalankan model, lalu mengembalikan hasil klasifikasi dan pesan penanganan.

## Prasyarat

- Python 3.10+ (disarankan)
- `pip`
- Dependensi pada file `/home/runner/work/ml-stunting/ml-stunting/requirements.txt`

## Instalasi

1. Masuk ke direktori proyek:
```bash
cd /home/runner/work/ml-stunting/ml-stunting
```
2. Instal dependensi:
```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

### Opsi 1 (sesuai konfigurasi `main.py`)
```bash
python main.py
```
Server berjalan pada `http://0.0.0.0:5000`.

### Opsi 2 (mode pengembangan dengan reload)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Server berjalan pada `http://0.0.0.0:8000`.

## Dokumentasi API

Setelah server aktif:
- Swagger UI: `http://localhost:<port>/docs`
- ReDoc: `http://localhost:<port>/redoc`

Ganti `<port>` sesuai mode menjalankan aplikasi (`5000` atau `8000`).

## Ringkasan Endpoint

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/` | Status layanan (root health check) |
| GET | `/health` | Pemeriksaan kesehatan API |
| POST | `/predict` | Prediksi status pertumbuhan anak |
| GET | `/model/info` | Informasi model prediksi |
| POST | `/recive` | Menerima data berat/tinggi dari perangkat IoT |
| POST | `/trigger/{did}` | Mengaktifkan status trigger perangkat |
| POST | `/reset/{did}` | Menghapus data perangkat dari memori sementara |
| GET | `/ws/status` | Ringkasan koneksi WebSocket dan status perangkat |
| GET | `/devices` | Daftar seluruh perangkat yang tercatat |
| GET | `/devices/{device_id}` | Detail data perangkat tertentu |
| WS | `/ws/data/{device_id}` | Streaming data perangkat secara periodik |

## Panduan Pemakaian yang Disarankan

1. **Pastikan layanan aktif** dengan mengecek endpoint `/health`.
2. **Kirim data perangkat** (jika memakai IoT) ke `/recive` secara berkala.
3. **Gunakan endpoint perangkat** (`/devices` dan `/ws/status`) untuk memantau ketersediaan data.
4. **Kirim data anak lengkap** ke `/predict` dengan format yang valid.
5. **Gunakan hasil prediksi sebagai dukungan keputusan awal**, lalu tetap lakukan verifikasi oleh tenaga kesehatan.

Praktik input yang baik:
- Gunakan format tanggal `YYYY-MM-DD`.
- Gunakan `jenis_kelamin` dengan nilai `L` atau `P`.
- Pastikan satuan konsisten: berat dalam kilogram, tinggi dalam sentimeter.
- Validasi data kosong atau nilai tidak wajar sebelum dikirim ke API.

## Contoh Request

### 1) Cek kesehatan layanan
```bash
curl http://localhost:5000/health
```

### 2) Kirim data dari perangkat IoT
```bash
curl -X POST "http://localhost:5000/recive" \
  -H "Content-Type: application/json" \
  -d '{
    "did": "IOT_001",
    "tb": 86.4,
    "bb": 11.2
  }'
```

### 3) Prediksi status pertumbuhan anak
```bash
curl -X POST "http://localhost:5000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Anak A",
    "jenis_kelamin": "L",
    "bb_lahir": 3.1,
    "tb_lahir": 49.5,
    "tanggal_lahir": "2023-04-12",
    "berat": 11.2,
    "tinggi": 86.4
  }'
```

## Struktur Direktori Inti

```
/home/runner/work/ml-stunting/ml-stunting
├── main.py
├── requirements.txt
├── lib/
│   ├── main/
│   └── prediction/
├── models/
└── README.md
```

## Catatan Implementasi

- Penyimpanan data perangkat saat ini masih berbasis memori aplikasi (`data_devices`), belum persisten.
- CORS masih terbuka untuk semua origin dan perlu dikunci pada lingkungan produksi.
- Endpoint dan skema request/response dapat ditinjau langsung melalui Swagger untuk integrasi yang lebih presisi.
