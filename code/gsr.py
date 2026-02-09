# pip install SpeechRecognition

import speech_recognition as sr

def transkrip_audio_google(path_audio):
    # Inisialisasi recognizer
    recognizer = sr.Recognizer()

    # Membaca file audio
    try:
        with sr.AudioFile(path_audio) as source:
            print("Sedang memproses audio...")
            # Mengambil data audio
            audio_data = recognizer.record(source)

            # Melakukan transkripsi dengan Google Web Speech API
            # language='id-ID' adalah kode untuk Bahasa Indonesia
            text = recognizer.recognize_google(audio_data, language='id-ID')

            return text

    except sr.UnknownValueError:
        return "Error: Audio tidak jelas atau tidak ada suara yang terdeteksi."
    except sr.RequestError as e:
        return f"Error: Masalah koneksi ke layanan Google; {e}"
    except Exception as e:
        return f"Error: Terjadi kesalahan; {e}"


# --- Cara Penggunaan ---
# Pastikan Anda punya file audio format .wav
nama_file = "rekaman_saya.wav"

# Buat file dummy jika belum ada (opsional, hapus jika sudah punya file)
# Atau ganti 'rekaman_saya.wav' dengan path file audio Anda
print(f"Hasil Transkripsi:\n{transkrip_audio_google(nama_file)}")