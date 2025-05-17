import json
import os
from openai import OpenAI

# API key dan base URL untuk model AI
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"

# Inisialisasi klien OpenAI
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Konfigurasi untuk bahasa yang didukung
SUPPORTED_LANGUAGES = {
    "id": {
        "name": "Indonesia",
        "code": "id",
        "system_prompt": "Anda adalah tutor bahasa Indonesia yang ramah dan membantu. Bantu pengguna meningkatkan kemampuan berbahasa Indonesia mereka. Jawab dalam bahasa Indonesia.",
        "language_level_names": {
            "beginner": "Pemula",
            "intermediate": "Menengah",
            "advanced": "Lanjutan"
        }
    },
    "en": {
        "name": "English",
        "code": "en",
        "system_prompt": "You are a friendly and helpful English language tutor. Help the user improve their English language skills. Answer in English.",
        "language_level_names": {
            "beginner": "Beginner",
            "intermediate": "Intermediate",
            "advanced": "Advanced"
        }
    },
    "jp": {
        "name": "日本語",
        "code": "jp",
        "system_prompt": "あなたは親切な日本語教師です。ユーザーが日本語能力を向上させるのを手伝ってください。日本語で答えてください。",
        "language_level_names": {
            "beginner": "初級",
            "intermediate": "中級",
            "advanced": "上級"
        }
    }
}

def get_supported_languages():
    """
    Mendapatkan daftar bahasa yang didukung oleh tutor virtual
    
    Returns:
        dict: Dictionary berisi bahasa-bahasa yang didukung
    """
    return {code: {"name": lang["name"]} for code, lang in SUPPORTED_LANGUAGES.items()}

def generate_chat_response(user_message, language_code, language_level, conversation_context=None, exercise_type="free_conversation"):
    """
    Menghasilkan respons chat dari tutor virtual AI
    
    Args:
        user_message (str): Pesan dari pengguna
        language_code (str): Kode bahasa (id, en, jp)
        language_level (str): Level kemampuan bahasa (beginner, intermediate, advanced)
        conversation_context (list): Riwayat percakapan
        exercise_type (str): Jenis latihan (free_conversation, writing_exercise, speaking_practice)
        
    Returns:
        dict: Respons dari tutor virtual AI
    """
    if language_code not in SUPPORTED_LANGUAGES:
        return {
            "response": "Bahasa tidak didukung.",
            "error": True
        }
    
    if conversation_context is None:
        conversation_context = []
    
    # Menyiapkan prompt sistem berdasarkan jenis latihan dan level bahasa
    language_config = SUPPORTED_LANGUAGES[language_code]
    system_prompt = language_config["system_prompt"]
    level_name = language_config["language_level_names"].get(language_level, "Pemula")
    
    # Menambahkan instruksi khusus berdasarkan jenis latihan
    if exercise_type == "writing_exercise":
        system_prompt += f"\nAnda mengajar pengguna pada level {level_name}. Berikan latihan menulis yang sesuai dengan level mereka. Saat pengguna mengirimkan tulisan, berikan koreksi yang jelas dan feedback yang membangun. Fokus pada kesalahan tata bahasa, pilihan kata, dan struktur kalimat. Sebutkan perbaikan spesifik dan berikan contoh alternatif yang lebih baik."
    elif exercise_type == "speaking_practice":
        system_prompt += f"\nAnda mengajar pengguna pada level {level_name}. Berikan latihan berbicara yang sesuai dengan level mereka. Saat pengguna mengirimkan pesan, anggap itu adalah transkrip dari apa yang mereka ucapkan. Berikan koreksi pada pengucapan dan intonasi berdasarkan kalimat yang mereka tulis. Berikan contoh frasa atau kalimat pendek yang dapat diucapkan dengan benar."
    else:  # free_conversation
        system_prompt += f"\nAnda mengajar pengguna pada level {level_name}. Lakukan percakapan alami dengan pengguna sesuai dengan level bahasa mereka. Gunakan kata-kata dan struktur kalimat yang sesuai dengan level mereka. Jika pengguna membuat kesalahan, berikan koreksi ringan tanpa mengganggu alur percakapan."
    
    # Membangun daftar pesan untuk API
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Menambahkan riwayat percakapan (maksimal 5 pesan terakhir)
    for msg in conversation_context[-5:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Menambahkan pesan pengguna
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Memanggil OpenAI API
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",  # Bisa diganti dengan model lain yang didukung OpenRouter
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        assistant_response = response.choices[0].message.content
        
        # Jika latihan menulis, berikan analisis dan koreksi
        if exercise_type == "writing_exercise":
            # Berikan analisis tambahan untuk latihan menulis
            analysis_prompt = f"Analisis teks berikut dari pembelajar bahasa level {level_name}:\n\n{user_message}\n\nBerikan: 1) Skor (1-10), 2) Kekuatan, 3) Area yang perlu ditingkatkan, 4) Versi yang diperbaiki"
            
            analysis_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            analysis_response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=analysis_messages,
                temperature=0.7,
                max_tokens=800
            )
            
            analysis_text = analysis_response.choices[0].message.content
            
            # Gabungkan respons asisten dengan analisis
            return {
                "response": assistant_response,
                "analysis": analysis_text,
                "error": False
            }
        
        return {
            "response": assistant_response,
            "error": False
        }
        
    except Exception as e:
        print(f"Error in virtual tutor: {str(e)}")
        return {
            "response": f"Maaf, terjadi kesalahan saat berkomunikasi dengan tutor virtual: {str(e)}",
            "error": True
        }

def generate_speaking_feedback(transcription, language_code, language_level):
    """
    Menghasilkan umpan balik untuk latihan speaking berdasarkan transkrip
    
    Args:
        transcription (str): Transkrip audio dari pengguna
        language_code (str): Kode bahasa (id, en, jp)
        language_level (str): Level kemampuan bahasa (beginner, intermediate, advanced)
        
    Returns:
        dict: Umpan balik untuk kemampuan berbicara pengguna
    """
    if language_code not in SUPPORTED_LANGUAGES:
        return {
            "feedback": "Bahasa tidak didukung.",
            "error": True
        }
    
    language_config = SUPPORTED_LANGUAGES[language_code]
    system_prompt = language_config["system_prompt"]
    level_name = language_config["language_level_names"].get(language_level, "Pemula")
    
    prompt = f"""Sebagai tutor bahasa untuk level {level_name}, analisis transkrip speaking berikut:

Transkrip: "{transcription}"

Berikan:
1. Skor keseluruhan (1-10)
2. Kekuatan dalam berbicara
3. Area yang perlu ditingkatkan
4. Saran perbaikan yang spesifik
5. Contoh frasa atau kalimat yang benar
"""
    
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        feedback = response.choices[0].message.content
        
        return {
            "feedback": feedback,
            "error": False
        }
        
    except Exception as e:
        print(f"Error generating speaking feedback: {str(e)}")
        return {
            "feedback": f"Maaf, terjadi kesalahan saat menghasilkan umpan balik: {str(e)}",
            "error": True
        }

def get_conversation_topics(language_code, language_level):
    """
    Mendapatkan topik-topik percakapan yang direkomendasikan
    
    Args:
        language_code (str): Kode bahasa (id, en, jp)
        language_level (str): Level kemampuan bahasa (beginner, intermediate, advanced)
        
    Returns:
        list: Daftar topik percakapan yang direkomendasikan
    """
    if language_code not in SUPPORTED_LANGUAGES:
        return []
    
    language_config = SUPPORTED_LANGUAGES[language_code]
    level_name = language_config["language_level_names"].get(language_level, "Pemula")
    
    # Topik percakapan berdasarkan level bahasa
    topics = {
        "beginner": [
            "Perkenalan diri",
            "Keluarga",
            "Hobi dan aktivitas",
            "Makanan favorite",
            "Rutinitas harian"
        ],
        "intermediate": [
            "Pengalaman perjalanan",
            "Film dan acara TV",
            "Budaya lokal",
            "Pendidikan",
            "Teknologi dalam kehidupan sehari-hari"
        ],
        "advanced": [
            "Isu-isu sosial",
            "Lingkungan dan keberlanjutan",
            "Politik dan kebijakan publik",
            "Seni dan literatur",
            "Filosofi dan etika"
        ]
    }
    
    return topics.get(language_level, topics["beginner"])

def get_writing_prompts(language_code, language_level):
    """
    Mendapatkan prompt untuk latihan menulis
    
    Args:
        language_code (str): Kode bahasa (id, en, jp)
        language_level (str): Level kemampuan bahasa (beginner, intermediate, advanced)
        
    Returns:
        list: Daftar prompt untuk latihan menulis
    """
    if language_code not in SUPPORTED_LANGUAGES:
        return []
    
    # Mengambil prompt menulis yang sesuai dengan bahasa dan level
    if language_code == "id":
        prompts = {
            "beginner": [
                "Ceritakan tentang diri Anda dan keluarga Anda.",
                "Tuliskan aktivitas Anda selama akhir pekan.",
                "Deskripsikan rumah atau apartemen Anda.",
                "Apa makanan favorit Anda dan bagaimana cara membuatnya?",
                "Tuliskan tentang hobi Anda."
            ],
            "intermediate": [
                "Bagaimana teknologi telah mengubah hidup kita?",
                "Ceritakan pengalaman liburan yang berkesan.",
                "Apa pendapat Anda tentang sistem pendidikan saat ini?",
                "Bandingkan kehidupan di desa dan di kota.",
                "Tuliskan tentang film atau buku favorit Anda."
            ],
            "advanced": [
                "Bagaimana solusi untuk mengatasi masalah lingkungan di Indonesia?",
                "Analisis dampak media sosial terhadap hubungan interpersonal.",
                "Diskusikan peran pendidikan dalam mengurangi kesenjangan sosial.",
                "Tuliskan esai tentang pentingnya pelestarian budaya lokal di era globalisasi.",
                "Bagaimana teknologi AI dapat mempengaruhi masa depan pekerjaan?"
            ]
        }
    elif language_code == "en":
        prompts = {
            "beginner": [
                "Write about yourself and your family.",
                "Describe your daily routine.",
                "What is your favorite hobby and why?",
                "Write about a place you like to visit.",
                "Describe your best friend."
            ],
            "intermediate": [
                "How has technology changed our lives?",
                "Write about a memorable vacation experience.",
                "What are the advantages and disadvantages of social media?",
                "Compare life in the city and in the countryside.",
                "Describe a book or movie that influenced you."
            ],
            "advanced": [
                "Discuss the impact of artificial intelligence on future employment.",
                "Analyze the effectiveness of current environmental policies.",
                "What role should government play in education?",
                "Write an essay on the balance between privacy and security in the digital age.",
                "Discuss the importance of cultural preservation in the era of globalization."
            ]
        }
    elif language_code == "jp":
        prompts = {
            "beginner": [
                "自己紹介してください。",
                "あなたの一日の予定について書いてください。",
                "あなたの趣味は何ですか？",
                "あなたの家族について書いてください。",
                "好きな食べ物について書いてください。"
            ],
            "intermediate": [
                "テクノロジーは私たちの生活をどのように変えましたか？",
                "印象に残った旅行体験について書いてください。",
                "SNSの長所と短所は何ですか？",
                "都会と田舎の生活を比較してください。",
                "あなたに影響を与えた本や映画について説明してください。"
            ],
            "advanced": [
                "人工知能が将来の雇用に与える影響について議論してください。",
                "現在の環境政策の有効性を分析してください。",
                "教育において政府はどのような役割を果たすべきですか？",
                "デジタル時代のプライバシーとセキュリティのバランスについてエッセイを書いてください。",
                "グローバル化時代における文化保存の重要性について議論してください。"
            ]
        }
    else:
        return []
    
    return prompts.get(language_level, prompts["beginner"])

def get_speaking_topics(language_code, language_level):
    """
    Mendapatkan topik untuk latihan berbicara
    
    Args:
        language_code (str): Kode bahasa (id, en, jp)
        language_level (str): Level kemampuan bahasa (beginner, intermediate, advanced)
        
    Returns:
        list: Daftar topik untuk latihan berbicara
    """
    if language_code not in SUPPORTED_LANGUAGES:
        return []
    
    # Mengambil topik berbicara yang sesuai dengan bahasa dan level
    if language_code == "id":
        topics = {
            "beginner": [
                "Perkenalan diri dalam 1 menit",
                "Ceritakan tentang keluarga Anda",
                "Deskripsikan kamar atau rumah Anda",
                "Apa yang Anda lakukan di akhir pekan?",
                "Ceritakan tentang makanan favorit Anda"
            ],
            "intermediate": [
                "Ceritakan tentang film yang baru-baru ini Anda tonton",
                "Bagaimana pendapat Anda tentang media sosial?",
                "Apa rencana Anda untuk masa depan?",
                "Ceritakan tentang tempat wisata di kota Anda",
                "Bagaimana Anda mengatasi stres?"
            ],
            "advanced": [
                "Bagaimana pendapat Anda tentang sistem pendidikan di Indonesia?",
                "Diskusikan isu lingkungan yang paling penting saat ini",
                "Bagaimana teknologi mengubah cara kita berkomunikasi?",
                "Berikan pendapat Anda tentang isu politik terkini",
                "Bagaimana cara mengatasi masalah kemacetan di kota-kota besar?"
            ]
        }
    elif language_code == "en":
        topics = {
            "beginner": [
                "Introduce yourself in 1 minute",
                "Talk about your family",
                "Describe your room or house",
                "What do you do on weekends?",
                "Talk about your favorite food"
            ],
            "intermediate": [
                "Talk about a movie you watched recently",
                "What's your opinion on social media?",
                "What are your plans for the future?",
                "Describe a tourist attraction in your city",
                "How do you deal with stress?"
            ],
            "advanced": [
                "What's your view on the education system in your country?",
                "Discuss the most important environmental issue today",
                "How has technology changed the way we communicate?",
                "Give your opinion on a current political issue",
                "How would you solve traffic problems in big cities?"
            ]
        }
    elif language_code == "jp":
        topics = {
            "beginner": [
                "1分間で自己紹介してください",
                "あなたの家族について話してください",
                "あなたの部屋や家について説明してください",
                "週末は何をしますか？",
                "好きな食べ物について話してください"
            ],
            "intermediate": [
                "最近見た映画について話してください",
                "SNSについてどう思いますか？",
                "将来の計画は何ですか？",
                "あなたの街の観光スポットについて説明してください",
                "ストレスにどう対処しますか？"
            ],
            "advanced": [
                "あなたの国の教育システムについてどう思いますか？",
                "今日の最も重要な環境問題について議論してください",
                "テクノロジーは私たちのコミュニケーション方法をどのように変えましたか？",
                "現在の政治問題についてあなたの意見を述べてください",
                "大都市の交通問題をどのように解決しますか？"
            ]
        }
    else:
        return []
    
    return topics.get(language_level, topics["beginner"]) 