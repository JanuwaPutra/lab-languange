import json
import random
import os
from datetime import datetime
from speech_recognition import Recognizer, AudioData
import base64
import io

# Fungsi-fungsi untuk tes penempatan
def get_placement_test():
    """
    Mengambil soal-soal tes penempatan.
    
    Returns:
        list: Daftar soal tes penempatan
    """
    # Dalam implementasi nyata, ini akan diambil dari database atau file konfigurasi
    # Ini adalah contoh struktur data
    questions = [
        {
            "id": "p1",
            "type": "multiple_choice",
            "question": "Pilih kata yang tepat untuk melengkapi kalimat berikut: Saya ___ ke sekolah setiap hari.",
            "options": ["pergi", "pergian", "berpergian", "kepergian"],
            "correct_answer": "pergi",
            "difficulty": "basic"
        },
        {
            "id": "p2",
            "type": "multiple_choice",
            "question": "Pilih kata yang tepat untuk melengkapi kalimat berikut: Dia ___ buku itu dengan cepat.",
            "options": ["baca", "membaca", "dibaca", "terbaca"],
            "correct_answer": "membaca",
            "difficulty": "basic"
        },
        {
            "id": "p3",
            "type": "multiple_choice",
            "question": "Pilih makna yang tepat untuk kata 'ambigu'.",
            "options": ["tidak jelas", "menakutkan", "menghibur", "membosankan"],
            "correct_answer": "tidak jelas",
            "difficulty": "intermediate"
        },
        {
            "id": "p4",
            "type": "fill_in_blank",
            "question": "Lengkapi dengan kata yang tepat: Para peneliti sedang ___ obat baru untuk penyakit tersebut.",
            "answer": "mengembangkan",
            "difficulty": "intermediate"
        },
        {
            "id": "p5",
            "type": "multiple_choice",
            "question": "Pilih kalimat yang menggunakan kata hubung yang tepat.",
            "options": [
                "Dia tidak datang karena dia sakit.",
                "Dia tidak datang tetapi dia sakit.",
                "Dia tidak datang atau dia sakit.",
                "Dia tidak datang jika dia sakit."
            ],
            "correct_answer": "Dia tidak datang karena dia sakit.",
            "difficulty": "advanced"
        }
    ]
    
    return questions

def evaluate_placement_test(answers):
    """
    Mengevaluasi jawaban tes penempatan untuk menentukan level pengguna.
    
    Args:
        answers (dict): Jawaban pengguna, dengan kunci berupa ID soal dan nilai berupa jawaban
        
    Returns:
        dict: Hasil evaluasi yang berisi skor, level, dan rekomendasi
    """
    # Mendapatkan soal-soal tes penempatan
    questions = get_placement_test()
    
    # Menghitung skor berdasarkan jawaban yang benar
    correct_count = 0
    total_questions = len(questions)
    results = []
    
    for question in questions:
        question_id = question["id"]
        user_answer = answers.get(question_id, "")
        
        if question["type"] == "multiple_choice":
            is_correct = user_answer == question["correct_answer"]
        elif question["type"] == "fill_in_blank":
            # Untuk jawaban isian, kita lakukan pencocokan sederhana
            # Dalam implementasi nyata, bisa menggunakan NLP untuk pencocokan lebih cerdas
            is_correct = user_answer.lower() == question["answer"].lower()
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_id": question_id,
            "is_correct": is_correct,
            "difficulty": question["difficulty"]
        })
    
    # Menghitung skor dalam persentase
    score = (correct_count / total_questions) * 100
    
    # Menentukan level berdasarkan skor
    if score < 40:
        level = "basic"
        recommendation = "Disarankan untuk memulai dari materi dasar."
    elif score < 70:
        level = "intermediate"
        recommendation = "Anda sudah memiliki pemahaman dasar. Lanjutkan dengan materi tingkat menengah."
    else:
        level = "advanced"
        recommendation = "Anda memiliki pemahaman yang baik. Lanjutkan dengan materi tingkat lanjut."
    
    return {
        "score": score,
        "level": level,
        "recommendation": recommendation,
        "details": results
    }

# Fungsi-fungsi untuk tes listening
def get_listening_test():
    """
    Mengambil soal-soal tes listening.
    
    Returns:
        list: Daftar soal tes listening
    """
    # Dalam implementasi nyata, ini akan diambil dari database atau file konfigurasi
    questions = [
        {
            "id": "l1",
            "type": "audio_comprehension",
            "audio_url": "/static/audio/listening/basic_conversation.mp3",
            "question": "Apa topik pembicaraan dalam rekaman tersebut?",
            "options": ["Cuaca", "Liburan", "Pekerjaan", "Keluarga"],
            "correct_answer": "Liburan",
            "difficulty": "basic",
            "transcript": "A: Apa rencana liburanmu minggu depan?\nB: Saya berencana mengunjungi pantai di Bali."
        },
        {
            "id": "l2",
            "type": "audio_comprehension",
            "audio_url": "/static/audio/listening/weather_report.mp3",
            "question": "Bagaimana prakiraan cuaca untuk besok menurut rekaman?",
            "options": ["Hujan", "Cerah", "Berawan", "Badai"],
            "correct_answer": "Cerah",
            "difficulty": "basic",
            "transcript": "Prakiraan cuaca untuk besok adalah cerah sepanjang hari dengan suhu sekitar 28 derajat Celsius."
        },
        {
            "id": "l3",
            "type": "audio_comprehension",
            "audio_url": "/static/audio/listening/news_report.mp3",
            "question": "Apa peristiwa utama yang diberitakan dalam rekaman?",
            "options": ["Bencana alam", "Pertemuan politik", "Acara olahraga", "Penemuan ilmiah"],
            "correct_answer": "Acara olahraga",
            "difficulty": "intermediate",
            "transcript": "Tim nasional sepak bola Indonesia berhasil meraih kemenangan dengan skor 2-0 dalam pertandingan persahabatan melawan Malaysia kemarin."
        }
    ]
    
    return questions

def evaluate_listening(answers):
    """
    Mengevaluasi jawaban tes listening.
    
    Args:
        answers (dict): Jawaban pengguna, dengan kunci berupa ID soal dan nilai berupa jawaban
        
    Returns:
        dict: Hasil evaluasi yang berisi skor dan level
    """
    # Mendapatkan soal-soal tes listening
    questions = get_listening_test()
    
    # Menghitung skor berdasarkan jawaban yang benar
    correct_count = 0
    total_questions = len(questions)
    results = []
    
    for question in questions:
        question_id = question["id"]
        user_answer = answers.get(question_id, "")
        
        is_correct = user_answer == question["correct_answer"]
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_id": question_id,
            "is_correct": is_correct,
            "difficulty": question["difficulty"],
            "transcript": question.get("transcript", "")
        })
    
    # Menghitung skor dalam persentase
    score = (correct_count / total_questions) * 100
    
    # Menentukan level berdasarkan skor
    if score < 40:
        level = "basic"
        feedback = "Anda perlu lebih banyak latihan mendengarkan. Cobalah untuk mendengarkan percakapan sederhana."
    elif score < 70:
        level = "intermediate"
        feedback = "Kemampuan mendengarkan Anda cukup baik. Lanjutkan dengan latihan pada topik yang lebih beragam."
    else:
        level = "advanced"
        feedback = "Kemampuan mendengarkan Anda sangat baik. Lanjutkan dengan latihan pada materi yang lebih kompleks."
    
    return {
        "score": score,
        "level": level,
        "feedback": feedback,
        "details": results
    }

# Fungsi-fungsi untuk tes reading
def get_reading_test():
    """
    Mengambil soal-soal tes reading.
    
    Returns:
        list: Daftar soal tes reading
    """
    # Dalam implementasi nyata, ini akan diambil dari database atau file konfigurasi
    questions = [
        {
            "id": "r1",
            "type": "passage_comprehension",
            "passage": "Kucing adalah hewan mamalia karnivora dari keluarga Felidae. Kata 'kucing' biasanya mengacu kepada 'kucing' yang telah dijinakkan, tetapi bisa juga mengacu kepada 'kucing besar' seperti singa dan harimau.",
            "question": "Apa jenis hewan kucing menurut teks?",
            "options": ["Herbivora", "Karnivora", "Omnivora", "Insektivora"],
            "correct_answer": "Karnivora",
            "difficulty": "basic"
        },
        {
            "id": "r2",
            "type": "passage_comprehension",
            "passage": "Energi terbarukan adalah energi yang berasal dari sumber daya alam yang dapat diperbarui seperti matahari, angin, air, dan panas bumi. Energi terbarukan memiliki dampak lingkungan yang minimal dibandingkan dengan energi fosil.",
            "question": "Manakah yang BUKAN merupakan sumber energi terbarukan menurut teks?",
            "options": ["Matahari", "Angin", "Batu bara", "Panas bumi"],
            "correct_answer": "Batu bara",
            "difficulty": "intermediate"
        },
        {
            "id": "r3",
            "type": "passage_comprehension",
            "passage": "Kecerdasan buatan (Artificial Intelligence/AI) adalah kecerdasan yang didemonstrasikan oleh mesin, berbeda dengan kecerdasan alami yang ditunjukkan oleh manusia. AI dapat dibagi menjadi dua kategori utama: AI lemah, yang dirancang untuk melakukan tugas tertentu, dan AI kuat, yang dapat melakukan tugas intelektual apa pun yang dapat dilakukan manusia.",
            "question": "Apa perbedaan utama antara AI lemah dan AI kuat menurut teks?",
            "options": [
                "AI lemah lebih mudah dibuat daripada AI kuat",
                "AI lemah hanya untuk tugas tertentu, AI kuat untuk tugas apa pun",
                "AI lemah menggunakan lebih sedikit daya komputasi",
                "AI lemah tidak secerdas AI kuat"
            ],
            "correct_answer": "AI lemah hanya untuk tugas tertentu, AI kuat untuk tugas apa pun",
            "difficulty": "advanced"
        }
    ]
    
    return questions

def evaluate_reading(answers):
    """
    Mengevaluasi jawaban tes reading.
    
    Args:
        answers (dict): Jawaban pengguna, dengan kunci berupa ID soal dan nilai berupa jawaban
        
    Returns:
        dict: Hasil evaluasi yang berisi skor dan level
    """
    # Mendapatkan soal-soal tes reading
    questions = get_reading_test()
    
    # Menghitung skor berdasarkan jawaban yang benar
    correct_count = 0
    total_questions = len(questions)
    results = []
    
    for question in questions:
        question_id = question["id"]
        user_answer = answers.get(question_id, "")
        
        is_correct = user_answer == question["correct_answer"]
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_id": question_id,
            "is_correct": is_correct,
            "difficulty": question["difficulty"]
        })
    
    # Menghitung skor dalam persentase
    score = (correct_count / total_questions) * 100
    
    # Menentukan level berdasarkan skor
    if score < 40:
        level = "basic"
        feedback = "Anda perlu lebih banyak latihan membaca. Mulailah dengan teks sederhana."
    elif score < 70:
        level = "intermediate"
        feedback = "Kemampuan membaca Anda cukup baik. Lanjutkan dengan latihan pada teks yang lebih beragam."
    else:
        level = "advanced"
        feedback = "Kemampuan membaca Anda sangat baik. Lanjutkan dengan latihan pada teks yang lebih kompleks."
    
    return {
        "score": score,
        "level": level,
        "feedback": feedback,
        "details": results
    }

# Fungsi-fungsi untuk tes speaking
def get_speaking_test():
    """
    Mengambil soal-soal tes speaking.
    
    Returns:
        list: Daftar soal tes speaking
    """
    # Dalam implementasi nyata, ini akan diambil dari database atau file konfigurasi
    questions = [
        {
            "id": "s1",
            "type": "pronunciation",
            "instruction": "Bacalah kalimat berikut dengan jelas:",
            "text": "Selamat pagi, nama saya adalah John.",
            "difficulty": "basic"
        },
        {
            "id": "s2",
            "type": "question_response",
            "instruction": "Jawablah pertanyaan berikut:",
            "question": "Apa kegiatan yang Anda sukai di waktu luang?",
            "example_answer": "Di waktu luang, saya suka membaca buku dan menonton film.",
            "difficulty": "basic"
        },
        {
            "id": "s3",
            "type": "describe_image",
            "instruction": "Jelaskan gambar berikut dengan detail:",
            "image_url": "/static/images/speaking/city_scene.jpg",
            "time_limit": 60,
            "difficulty": "intermediate"
        },
        {
            "id": "s4",
            "type": "express_opinion",
            "instruction": "Berikan pendapat Anda tentang topik berikut:",
            "topic": "Apakah teknologi digital memiliki dampak positif atau negatif terhadap pendidikan?",
            "time_limit": 90,
            "difficulty": "advanced"
        }
    ]
    
    return questions

def evaluate_speaking(audio_data, test_id):
    """
    Mengevaluasi rekaman suara untuk tes speaking.
    
    Args:
        audio_data (str): Data audio dalam format base64
        test_id (str): ID soal yang dijawab
        
    Returns:
        dict: Hasil evaluasi yang berisi skor, level, dan feedback
    """
    # Mendapatkan soal speaking berdasarkan test_id
    all_questions = get_speaking_test()
    question = next((q for q in all_questions if q["id"] == test_id), None)
    
    if not question:
        return {"error": "Soal tidak ditemukan"}
    
    # Proses audio data
    if ',' in audio_data:
        audio_data = audio_data.split(',')[1]
    
    # Dalam implementasi nyata, audio akan diproses menggunakan speech recognition dan NLP
    # Untuk contoh ini, kita gunakan logika sederhana
    
    # Simulasi hasil analisis
    pronunciation_score = random.uniform(0.6, 0.95)  # Simulasi skor pengucapan antara 0.6-0.95
    fluency_score = random.uniform(0.5, 0.9)         # Simulasi skor kelancaran antara 0.5-0.9
    content_score = random.uniform(0.7, 1.0)         # Simulasi skor konten antara 0.7-1.0
    
    # Menghitung skor keseluruhan
    overall_score = (pronunciation_score + fluency_score + content_score) / 3 * 100
    
    # Menentukan level berdasarkan skor
    if overall_score < 60:
        level = "basic"
        feedback = "Perlu latihan lebih banyak dalam pengucapan dan kelancaran berbicara."
    elif overall_score < 80:
        level = "intermediate"
        feedback = "Kemampuan berbicara Anda cukup baik. Lanjutkan latihan untuk meningkatkan kelancaran."
    else:
        level = "advanced"
        feedback = "Kemampuan berbicara Anda sangat baik. Anda dapat mencoba topik yang lebih kompleks."
    
    return {
        "score": overall_score,
        "level": level,
        "feedback": feedback,
        "details": {
            "pronunciation": pronunciation_score * 100,
            "fluency": fluency_score * 100,
            "content": content_score * 100
        }
    }

# Fungsi untuk laporan perkembangan
def generate_progress_report(placement_result, test_results):
    """
    Membuat laporan perkembangan berdasarkan hasil tes.
    
    Args:
        placement_result (dict): Hasil tes penempatan
        test_results (dict): Hasil tes kemampuan (listening, reading, speaking)
        
    Returns:
        dict: Laporan perkembangan
    """
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "placement": placement_result,
        "skills": test_results,
        "overall_level": None,
        "recommendations": []
    }
    
    # Menghitung level keseluruhan
    levels = []
    if placement_result:
        levels.append(placement_result.get("level"))
    
    for skill, result in test_results.items():
        levels.append(result.get("level"))
    
    # Menentukan level keseluruhan berdasarkan mayoritas
    if levels:
        level_counts = {"basic": 0, "intermediate": 0, "advanced": 0}
        for level in levels:
            if level in level_counts:
                level_counts[level] += 1
        
        max_level = max(level_counts.items(), key=lambda x: x[1])[0]
        report["overall_level"] = max_level
    
    # Membuat rekomendasi berdasarkan hasil
    if "listening" in test_results:
        listening_level = test_results["listening"].get("level")
        if listening_level == "basic":
            report["recommendations"].append("Latihan mendengarkan percakapan sederhana setiap hari.")
        elif listening_level == "intermediate":
            report["recommendations"].append("Cobalah mendengarkan podcast atau berita dalam bahasa target.")
    
    if "reading" in test_results:
        reading_level = test_results["reading"].get("level")
        if reading_level == "basic":
            report["recommendations"].append("Bacalah artikel sederhana atau cerita pendek setiap hari.")
        elif reading_level == "intermediate":
            report["recommendations"].append("Lanjutkan dengan membaca novel atau artikel ilmiah populer.")
    
    if "speaking" in test_results:
        speaking_level = test_results["speaking"].get("level")
        if speaking_level == "basic":
            report["recommendations"].append("Latihan berbicara dengan frasa dan kalimat sederhana setiap hari.")
        elif speaking_level == "intermediate":
            report["recommendations"].append("Cobalah berdiskusi dengan penutur asli atau bergabung dengan kelompok percakapan.")
    
    return report 