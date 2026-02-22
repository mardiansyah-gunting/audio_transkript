# pip install python-docx
# pip install SpeechRecognition
# pip install pydub

import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
import os
from docx import Document


def transkrip_audio_panjang(path_audio):
    recognizer = sr.Recognizer()
    teks_lengkap = []

    print(f"Memuat file: {path_audio}")
    try:
        if path_audio.lower().endswith('.m4a'):
            audio = AudioSegment.from_file(path_audio, format="m4a")
        else:
            audio = AudioSegment.from_file(path_audio)

        audio = audio.set_channels(1).set_frame_rate(16000)

    except Exception as e:
        return f"Error saat memuat/mengonversi audio: {e}"

    panjang_potongan_ms = 45000
    potongan_audio = make_chunks(audio, panjang_potongan_ms)

    print(f"Audio dipecah menjadi {len(potongan_audio)} bagian untuk diproses...\n")

    for i, chunk in enumerate(potongan_audio):
        nama_file_temp = f"temp_chunk_{i}.wav"
        chunk.export(nama_file_temp, format="wav")

        print(f"Memproses bagian {i + 1} dari {len(potongan_audio)}...")

        try:
            with sr.AudioFile(nama_file_temp) as source:
                audio_data = recognizer.record(source)
                teks = recognizer.recognize_google(audio_data, language='id-ID')
                teks_lengkap.append(teks)

        except sr.UnknownValueError:
            print(f" -> Bagian {i + 1}: Tidak ada suara yang jelas.")
        except sr.RequestError as e:
            print(f" -> Bagian {i + 1}: Error API ({e})")
        except Exception as e:
            print(f" -> Bagian {i + 1}: Error tidak terduga ({e})")

        finally:
            if os.path.exists(nama_file_temp):
                os.remove(nama_file_temp)

    hasil_akhir = " ".join(teks_lengkap)

    if not hasil_akhir:
        return ""

    return hasil_akhir


def simpan_ke_word(teks, path_simpan):
    doc = Document()
    doc.add_heading('Hasil Transkripsi Audio', 0)

    doc.add_paragraph(teks)

    doc.save(path_simpan)
    print(f"\nBerhasil! File Word tersimpan di: {path_simpan}")


nama_file = '/Users/mardiansyahgunting/Repo/audio_transkript/audio_input/katamso/Jalan Brigjen Katamso 3.m4a'

nama_file_word = '/Users/mardiansyahgunting/Repo/audio_transkript/docx/katamso/Hasil_Transkripsi_Katamso-3.docx'

print("=" * 50)
print("Memulai proses transkripsi...")
hasil = transkrip_audio_panjang(nama_file)

if hasil:
    # Jika transkripsi berhasil dan ada teksnya, simpan ke Word
    simpan_ke_word(hasil, nama_file_word)
else:
    print("\nProses dibatalkan karena gagal mendapatkan teks dari audio.")
print("=" * 50)