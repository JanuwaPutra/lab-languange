import json
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample question data
# In a real implementation, this would be loaded from a database
QUESTIONS = {
    'id': [
        # Level 1 - Beginner
        [
            {
                "id": "id-l1-q1",
                "text": "Apa bahasa resmi Indonesia?",
                "options": ["Bahasa Indonesia", "Bahasa Inggris", "Bahasa Jawa", "Bahasa Sunda"],
                "answer": "Bahasa Indonesia",
                "explanation": "Bahasa Indonesia adalah bahasa resmi Republik Indonesia."
            },
            {
                "id": "id-l1-q2",
                "text": "Lengkapi kalimat: Saya ___ ke sekolah setiap hari.",
                "options": ["pergi", "pergian", "perpergian", "berpergian"],
                "answer": "pergi",
                "explanation": "Kata 'pergi' adalah kata kerja yang tepat untuk melengkapi kalimat tersebut."
            },
            {
                "id": "id-l1-q3",
                "text": "Manakah kata sifat di bawah ini?",
                "options": ["cantik", "makan", "mereka", "cepat-cepat"],
                "answer": "cantik",
                "explanation": "Cantik adalah kata sifat yang menjelaskan keadaan atau kualitas."
            }
        ],
        # Level 2 - Intermediate
        [
            {
                "id": "id-l2-q1",
                "text": "Manakah kalimat yang menggunakan kata hubung dengan benar?",
                "options": [
                    "Dia tidak datang karena dia sakit.",
                    "Dia tidak datang tapi dia sakit.",
                    "Dia tidak datang dan dia sakit.",
                    "Dia tidak datang atau dia sakit."
                ],
                "answer": "Dia tidak datang karena dia sakit.",
                "explanation": "Kata hubung 'karena' menunjukkan hubungan sebab-akibat antara tidak datang dan sakit."
            },
            {
                "id": "id-l2-q2",
                "text": "Imbuhan mana yang tepat untuk kata 'ajar' dalam konteks 'orang yang mengajar'?",
                "options": ["pe-", "peng-", "pem-", "per-"],
                "answer": "peng-",
                "explanation": "Imbuhan 'peng-' pada kata dasar 'ajar' membentuk kata 'pengajar' yang berarti orang yang mengajar."
            },
            {
                "id": "id-l2-q3",
                "text": "Bentuk jamak dari kata 'anak' dalam bahasa Indonesia yang benar adalah...",
                "options": ["anak-anak", "para anak", "anaks", "anak semua"],
                "answer": "anak-anak",
                "explanation": "Dalam bahasa Indonesia, bentuk jamak dapat dibuat dengan pengulangan kata, seperti 'anak-anak'."
            }
        ],
        # Level 3 - Advanced
        [
            {
                "id": "id-l3-q1",
                "text": "Kalimat manakah yang mengandung majas personifikasi?",
                "options": [
                    "Angin berbisik di telinga saya.",
                    "Dia seperti harimau ketika marah.",
                    "Rumahnya sangat besar sekali.",
                    "Mereka tertawa terbahak-bahak."
                ],
                "answer": "Angin berbisik di telinga saya.",
                "explanation": "Personifikasi adalah majas yang memberikan sifat manusia pada benda mati. Angin tidak bisa 'berbisik', ini adalah sifat manusia."
            },
            {
                "id": "id-l3-q2",
                "text": "Dalam Ejaan Yang Disempurnakan (EYD), manakah penulisan gelar yang benar?",
                "options": [
                    "Dr. Ahmad, S.H., M.Hum.",
                    "DR Ahmad SH M.Hum",
                    "dr Ahmad, SH, M.HUM",
                    "Dr Ahmad S.H. M.Hum"
                ],
                "answer": "Dr. Ahmad, S.H., M.Hum.",
                "explanation": "Penulisan gelar yang benar menurut EYD menggunakan titik setelah singkatan dan koma setelah nama."
            },
            {
                "id": "id-l3-q3",
                "text": "Manakah yang merupakan contoh kalimat aktif?",
                "options": [
                    "Buku itu dibaca oleh siswa.",
                    "Siswa membaca buku itu.",
                    "Buku itu sedang dibaca.",
                    "Terdengar suara gemuruh dari kejauhan."
                ],
                "answer": "Siswa membaca buku itu.",
                "explanation": "Kalimat aktif adalah kalimat yang subjeknya melakukan tindakan. Pada kalimat tersebut, 'siswa' (subjek) melakukan tindakan 'membaca'."
            }
        ]
    ],
    'en': [
        # Level 1 - Beginner
        [
            {
                "id": "en-l1-q1",
                "text": "What is the plural form of 'child'?",
                "options": ["childs", "childen", "children", "child"],
                "answer": "children",
                "explanation": "The plural form of 'child' is 'children'. It's an irregular plural."
            },
            {
                "id": "en-l1-q2",
                "text": "Choose the correct pronoun: ___ are going to the park.",
                "options": ["I", "He", "She", "They"],
                "answer": "They",
                "explanation": "When referring to multiple people, we use the pronoun 'they'."
            },
            {
                "id": "en-l1-q3",
                "text": "Which is the correct verb form? She ___ to school every day.",
                "options": ["go", "goes", "going", "gone"],
                "answer": "goes",
                "explanation": "For third person singular (she, he, it) in the present simple, we add -s or -es to the verb."
            }
        ],
        # Level 2 - Intermediate
        [
            {
                "id": "en-l2-q1",
                "text": "Choose the correct tense: I ___ the movie last night.",
                "options": ["watch", "watching", "watched", "am watching"],
                "answer": "watched",
                "explanation": "For completed actions in the past, we use the past simple tense (watched)."
            },
            {
                "id": "en-l2-q2",
                "text": "What is the correct preposition? She arrived ___ the airport on time.",
                "options": ["in", "on", "at", "by"],
                "answer": "at",
                "explanation": "We use 'at' with specific locations like airports, stations, etc."
            },
            {
                "id": "en-l2-q3",
                "text": "Choose the correct phrasal verb: Can you ___ this form?",
                "options": ["fill in", "fill out", "fill up", "Both A and B are correct"],
                "answer": "Both A and B are correct",
                "explanation": "Both 'fill in' and 'fill out' mean to complete a form with information."
            }
        ],
        # Level 3 - Advanced
        [
            {
                "id": "en-l3-q1",
                "text": "Identify the correct subjunctive mood: The teacher insisted that the student ___ the assignment.",
                "options": ["completes", "complete", "completed", "completing"],
                "answer": "complete",
                "explanation": "After verbs like 'insist', 'recommend', 'suggest' in formal contexts, we use the subjunctive form, which is the base form of the verb (without -s)."
            },
            {
                "id": "en-l3-q2",
                "text": "Which sentence contains an Oxford comma?",
                "options": [
                    "I bought apples oranges and bananas.",
                    "I bought apples, oranges and bananas.",
                    "I bought apples, oranges, and bananas.",
                    "I bought apples and oranges and bananas."
                ],
                "answer": "I bought apples, oranges, and bananas.",
                "explanation": "The Oxford comma is the comma used after the penultimate item in a list of three or more items."
            },
            {
                "id": "en-l3-q3",
                "text": "Which sentence uses the passive voice correctly?",
                "options": [
                    "The experiment was conducted by the scientist.",
                    "The scientist conducted the experiment.",
                    "The experiment conducting by the scientist.",
                    "The scientist was conducted the experiment."
                ],
                "answer": "The experiment was conducted by the scientist.",
                "explanation": "In passive voice, the subject (the experiment) receives the action, and the agent (the scientist) is introduced with 'by'."
            }
        ]
    ]
}

def get_questions(level, count=3, language='id'):
    """
    Get questions based on user level
    """
    # Convert level to integer if it's not already
    level = int(level) if not isinstance(level, int) else level
    
    # Ensure level is between 1 and 3
    level = max(1, min(level, 3))
    
    # Get questions for the specified level and language
    available_questions = QUESTIONS.get(language, QUESTIONS['id'])[level-1]
    
    # Limit number of questions
    count = min(count, len(available_questions))
    
    # Randomly select questions if we want fewer than all available
    if count < len(available_questions):
        selected_questions = random.sample(available_questions, count)
    else:
        selected_questions = available_questions.copy()
    
    return selected_questions

def evaluate_answer(user_answer, question_id, current_level):
    """
    Evaluate user's answer and adjust level if needed
    """
    # Ensure current_level is an integer
    current_level = int(current_level) if not isinstance(current_level, int) else current_level
    
    # Find the question by ID
    question = None
    language = 'id'  # Default language
    
    # Determine language from question ID
    if question_id.startswith('en-'):
        language = 'en'
    
    # Find the question in all levels
    for level_index, level_questions in enumerate(QUESTIONS[language]):
        for q in level_questions:
            if q['id'] == question_id:
                question = q
                break
        if question:
            break
    
    if not question:
        return False, "Pertanyaan tidak ditemukan", current_level
    
    # Check if the answer is correct
    is_correct = user_answer == question['answer']
    
    # Prepare feedback
    if is_correct:
        feedback = "Benar! " + question['explanation'] if language == 'id' else "Correct! " + question['explanation']
    else:
        feedback = f"Salah. Jawaban yang benar adalah '{question['answer']}'. " + question['explanation'] if language == 'id' else f"Incorrect. The correct answer is '{question['answer']}'. " + question['explanation']
    
    # Adjust level based on performance
    # This is a simple adjustment logic. In a real implementation, 
    # you would use a more sophisticated algorithm that considers multiple factors
    new_level = current_level
    
    # If user gets a question right at their current level, consider increasing level
    if is_correct and current_level < 3:
        # Check if the question was from the current level
        question_level = int(question_id.split('-l')[1][0])
        if question_level == current_level:
            # Simple 50% chance to increase level if correct
            if random.random() > 0.5:
                new_level = current_level + 1
    
    # If user gets a question wrong, consider decreasing level
    elif not is_correct and current_level > 1:
        # Simple 50% chance to decrease level if incorrect
        if random.random() > 0.5:
            new_level = current_level - 1
    
    return is_correct, feedback, new_level 