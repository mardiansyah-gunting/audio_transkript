# pip install openai-whisper

import whisper

def transkrip_audio_whisper(path_audio):
    print("Memuat model Whisper (ini mungkin memakan waktu saat pertama kali)...")

    # Model options: 'tiny', 'base', 'small', 'medium', 'large'
    # 'base' adalah keseimbangan yang baik antara kecepatan dan akurasi
    model = whisper.load_model("base")

    print("Sedang mentranskripsi...")

    # Melakukan transkripsi
    # fp16=False digunakan agar kompatibel jika tidak menggunakan GPU (hanya CPU)
    result = model.transcribe(path_audio, language="id", fp16=False)

    return result["text"]


# --- Cara Penggunaan ---
# Whisper mendukung .mp3, .wav, .m4a, dll.
nama_file = "rekaman_rapat.mp3"

try:
    hasil = transkrip_audio_whisper(nama_file)
    print("\nHasil Transkripsi:")
    print("-" * 20)
    print(hasil)
except Exception as e:
    print(f"Terjadi kesalahan: {e}")