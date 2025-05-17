# Lab Bahasa AI - Sistem Asesmen dan Bimbingan

Sistem Lab Bahasa berbasis AI untuk asesmen dan bimbingan bahasa yang dilengkapi dengan:

1. **Koreksi Tata Bahasa Otomatis** - Menggunakan LLM, spaCy, dan T5 untuk mendeteksi dan memperbaiki kesalahan tata bahasa
2. **Speech-to-Text** - Konversi ucapan ke teks untuk latihan listening dan speaking
3. **Adaptive Learning** - Soal dan latihan yang disesuaikan dengan level pengguna

## Instalasi

1. Klon repositori ini
2. Buat virtual environment:
   ```
   python -m venv venv
   ```
3. Aktifkan virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependensi:
   ```
   pip install -r requirements.txt
   ```
5. Install model bahasa menggunakan script setup:
   ```
   python setup_models.py
   ```
   - Pilih model `id_core_news_sm` (opsi 1) jika ingin model yang lebih ringan
   - Pilih model `id_core_news_md` (opsi 2) untuk model yang lebih akurat (token Hugging Face sudah tersedia)
   - Opsi 3 untuk melewati instalasi model bahasa Indonesia
6. Instal ffmpeg (diperlukan untuk konversi audio):
   - Windows:
     - Gunakan Chocolatey: `choco install ffmpeg`
     - Atau download dari [situs resmi FFmpeg](https://ffmpeg.org/download.html)
   - macOS:
     - Gunakan Homebrew: `brew install ffmpeg`
   - Linux:
     - Ubuntu/Debian: `sudo apt install ffmpeg`
     - Fedora: `sudo dnf install ffmpeg`
7. Buat file `.env` dengan kunci API yang diperlukan

## Mengatasi Masalah Instalasi Model

### Error 401 Unauthorized

1. **Cara Termudah - Gunakan Model Kecil**:

   - Pilih opsi 1 (`id_core_news_sm`) saat menjalankan `setup_models.py`
   - Model ini tidak memerlukan login dan tersedia melalui GitHub

2. **Gunakan Token Hugging Face yang Sudah Tersedia**:

   - Pilih opsi 2 (`id_core_news_md`) saat menjalankan `setup_models.py`
   - Token Hugging Face sudah disediakan secara default
   - Tidak perlu lagi membuat akun atau token sendiri

3. **Menggunakan Token Hugging Face Anda Sendiri** (opsional):

   - Jika token default tidak berfungsi, Anda masih bisa menggunakan token sendiri
   - Buat akun di [huggingface.co](https://huggingface.co/join) jika belum memiliki
   - Buka [halaman token](https://huggingface.co/settings/tokens)
   - Buat token baru dengan izin "read"
   - Jalankan `python setup_models.py` dan pilih opsi 2
   - Masukkan token Anda saat diminta

4. **Tanpa Model Bahasa Indonesia**:
   - Pilih opsi 3 pada `setup_models.py` untuk melewati instalasi model bahasa Indonesia
   - Sistem akan menggunakan model bahasa Inggris sebagai fallback

### Masalah Model T5

Model T5 akan didownload otomatis saat pertama kali menjalankan aplikasi. Jika mengalami masalah:

1. Pastikan koneksi internet stabil
2. Jalankan aplikasi dengan `python app.py` dan biarkan beberapa menit untuk download model
3. Jika masih bermasalah, periksa ruang disk dan izin sistem

## Penggunaan

1. Jalankan aplikasi:
   ```
   python app.py
   ```
2. Buka browser dan akses http://localhost:5000

## Fitur

### Koreksi Tata Bahasa

- Deteksi kesalahan tata bahasa
- Saran perbaikan
- Penjelasan aturan tata bahasa

### Speech-to-Text

- Latihan pengucapan
- Evaluasi akurasi pengucapan
- Umpan balik untuk perbaikan

### Adaptive Learning

- Penilaian tingkat kemampuan
- Soal yang disesuaikan dengan level pengguna
- Analisis kemajuan belajar

## Teknologi

- Python
- Flask
- Transformers
- spaCy
- SpeechRecognition
- PyAudio
