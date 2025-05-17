import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize models
try:
    # Load spaCy models
    print("Loading spaCy models...")
    # Model bahasa Inggris
    nlp_en = spacy.load("en_core_web_sm")
    
    # Coba load model bahasa Indonesia jika tersedia
    try:
        # Coba load model yang lebih kecil terlebih dahulu
        nlp_id = spacy.load("xx_ent_wiki_sm")
        print("Model bahasa Indonesia (xx_ent_wiki_sm) berhasil dimuat")
    except OSError:
        try:
            # Jika tidak ada, coba id_core_news_md
            nlp_id = spacy.load("id_core_news_md")
            print("Model bahasa Indonesia (id_core_news_md) berhasil dimuat")
        except OSError:
            # Jika tidak ada model bahasa Indonesia, gunakan fallback ke model bahasa Inggris
            print("Model bahasa Indonesia tidak ditemukan. Gunakan perintah: python -m spacy download id_core_news_sm")
            print("Menggunakan model bahasa Inggris sebagai fallback untuk bahasa Indonesia")
            nlp_id = nlp_en
    
    # Load T5 model for grammar correction
    model_name = "t5-base"  # Can be changed to a larger model if needed
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    models_loaded = False

def analyze_text_with_spacy(text, language='id'):
    """
    Analyze text using spaCy to identify potential grammar issues
    """
    if not models_loaded:
        return [], "Model tidak dapat dimuat. Periksa instalasi."
    
    nlp = nlp_id if language == 'id' else nlp_en
    doc = nlp(text)
    
    issues = []
    
    # Check for basic grammar issues
    for i, token in enumerate(doc):
        # Check for subject-verb agreement in English
        if language == 'en' and token.pos_ == "VERB":
            # Simple subject-verb agreement check
            subjects = [t for t in token.children if t.dep_ == "nsubj"]
            if subjects and subjects[0].tag_ == "NNS" and token.tag_ in ["VBZ"]:
                issues.append({
                    "start": subjects[0].idx,
                    "end": token.idx + len(token.text),
                    "text": f"{subjects[0].text} {token.text}",
                    "suggestion": f"{subjects[0].text} {token.text.replace('s', '')}",
                    "rule": "Subject-verb agreement"
                })
        
        # Check for preposition misuse
        if token.pos_ == "ADP" and token.dep_ == "prep":
            # Example check for common preposition errors
            if language == 'id' and token.text == "di" and i < len(doc) - 1:
                next_token = doc[i+1]
                if next_token.pos_ == "VERB":
                    issues.append({
                        "start": token.idx,
                        "end": next_token.idx + len(next_token.text),
                        "text": f"{token.text} {next_token.text}",
                        "suggestion": next_token.text,
                        "rule": "Penggunaan preposisi 'di' sebelum kata kerja"
                    })
    
    return issues, doc.text

def correct_with_t5(text, language='id'):
    """
    Use T5 model to correct grammar
    """
    if not models_loaded:
        return text, "Model tidak dapat dimuat. Periksa instalasi."
    
    try:
        # Format input for T5
        task_prefix = "grammar: " if language == 'en' else "tata bahasa: "
        input_text = task_prefix + text
        
        # Tokenize and generate correction
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        # Meningkatkan parameter generasi untuk koreksi yang lebih agresif
        outputs = model.generate(
            input_ids, 
            max_length=512, 
            num_beams=5,  # Meningkatkan beam search
            do_sample=True,  # Aktifkan sampling
            top_k=50,  # Kontrol keberagaman
            top_p=0.95,  # Kontrol kualitas
            temperature=0.7,  # Tingkatkan kreatifitas sedikit
            early_stopping=True
        )
        
        corrected_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Log the output for debugging
        print(f"T5 Input: {input_text}")
        print(f"T5 Output: {corrected_text}")
        
        # If T5 output is identical to input or is just the task prefix, return original
        if corrected_text == text or corrected_text == input_text or corrected_text == task_prefix:
            return text, []
        
        # Jika model mengembalikan prefix yang berulang, bersihkan semuanya
        while corrected_text.startswith(task_prefix):
            corrected_text = corrected_text[len(task_prefix):].strip()
        
        # Periksa prefix berulang di tengah teks (khusus untuk masalah "tata bahasa:" berulang)
        if ": tata bahasa:" in corrected_text:
            parts = corrected_text.split(": tata bahasa:")
            corrected_text = parts[0]
        
        # Return the corrected text with a generic explanation
        return corrected_text, [{
            "text": text,
            "suggestion": corrected_text,
            "rule": "Koreksi otomatis oleh model T5"
        }]
    except Exception as e:
        print(f"Error in T5 correction: {e}")
        return text, []

def correct_informal_words(text, language='id'):
    """
    Koreksi untuk kata-kata informal menggunakan API OpenRouter
    """
    corrections = []
    corrected_text = text
    
    try:
        # Inisialisasi klien OpenRouter
        client = OpenAI(
            api_key="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",
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Siapkan prompt berdasarkan bahasa
        if language == 'id':
            system_prompt = "Anda adalah asisten koreksi kata informal bahasa Indonesia. Perbaiki kata-kata informal dalam teks berikut dan berikan daftar koreksi dengan format: teks asli|teks koreksi|alasan koreksi. Jangan berikan penjelasan tambahan."
        else:
            system_prompt = "You are an assistant for correcting informal words in English. Correct the informal words in the following text and provide a list of corrections in the format: original text|corrected text|reason for correction. Do not provide additional explanations."
        
        # Panggil API OpenRouter dengan model GPT-4o-mini
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        # Ambil hasil koreksi
        corrected_result = response.choices[0].message.content.strip()
        
        # Parse hasil koreksi dan buat daftar koreksi
        correction_lines = [line for line in corrected_result.split('\n') if '|' in line]
        
        for line in correction_lines:
            parts = line.split('|')
            if len(parts) >= 3:
                original, corrected, rule = parts[0].strip(), parts[1].strip(), parts[2].strip()
                
                # Temukan posisi teks asli
                index = text.find(original)
                if index >= 0:
                    corrections.append({
                        "start": index,
                        "end": index + len(original),
                        "text": original,
                        "suggestion": corrected,
                        "rule": rule
                    })
                    
                    # Update teks yang sudah dikoreksi
                    corrected_text = corrected_text.replace(original, corrected)
        
        # Jika tidak ada koreksi eksplisit tetapi ada hasil yang berbeda, gunakan hasil lengkap
        if not corrections and corrected_result != text:
            corrections.append({
                "start": 0,
                "end": len(text),
                "text": text,
                "suggestion": corrected_result,
                "rule": "Koreksi otomatis kata informal oleh GPT-4o-mini"
            })
            corrected_text = corrected_result
    
    except Exception as e:
        print(f"Error dalam koreksi kata informal: {e}")
    
    return corrected_text, corrections

def simulate_llm_correction(text, language='id'):
    """
    Koreksi tata bahasa menggunakan API OpenRouter dengan model GPT-4o-mini
    """
    corrections = []
    corrected_text = text
    
    try:
        # Inisialisasi klien OpenRouter
        client = OpenAI(
            api_key="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",  # API key OpenRouter
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Siapkan prompt berdasarkan bahasa
        if language == 'id':
            system_prompt = "Anda adalah asisten koreksi tata bahasa bahasa Indonesia. Perbaiki teks berikut dan berikan daftar koreksi dengan format: teks asli|teks koreksi|alasan koreksi. Jangan berikan penjelasan tambahan."
        else:
            system_prompt = "You are an English grammar correction assistant. Correct the following text and provide a list of corrections in the format: original text|corrected text|reason for correction. Do not provide additional explanations."
        
        # Panggil API OpenRouter dengan model GPT-4o-mini
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,  # Nilai rendah untuk hasil yang lebih deterministik
            max_tokens=1024
        )
        
        # Ambil hasil koreksi
        corrected_result = response.choices[0].message.content.strip()
        
        # Parse hasil koreksi dan buat daftar koreksi
        correction_lines = [line for line in corrected_result.split('\n') if '|' in line]
        
        for line in correction_lines:
            parts = line.split('|')
            if len(parts) >= 3:
                original, corrected, rule = parts[0].strip(), parts[1].strip(), parts[2].strip()
                
                # Temukan posisi teks asli
                index = text.find(original)
                if index >= 0:
                    corrections.append({
                        "start": index,
                        "end": index + len(original),
                        "text": original,
                        "suggestion": corrected,
                        "rule": rule
                    })
                    
                    # Update teks yang sudah dikoreksi
                    corrected_text = corrected_text.replace(original, corrected)
        
        # Jika tidak ada koreksi eksplisit tetapi ada hasil yang berbeda, gunakan hasil lengkap
        if not corrections and corrected_result != text:
            corrections.append({
                "start": 0,
                "end": len(text),
                "text": text,
                "suggestion": corrected_result,
                "rule": "Koreksi otomatis oleh GPT-4o-mini"
            })
            corrected_text = corrected_result
            
        # Pastikan output teks bersih dari prefix berulang
        corrected_text = clean_text_output(corrected_text, language)
            
        return corrected_text, corrections
        
    except Exception as e:
        print(f"Error menggunakan OpenRouter API: {e}")
        
        # Fallback ke simulasi sederhana jika API gagal
        fallback_corrections = []
        
        # if language == 'id':
        #     common_errors = {
        #         'di rumah nya': {'text': 'di rumahnya', 'rule': 'Penulisan kata ganti kepunyaan'},
        #         'tidak bisa di terima': {'text': 'tidak bisa diterima', 'rule': 'Penulisan awalan di-'},
        #         'belajar lah': {'text': 'belajarlah', 'rule': 'Penulisan partikel lah'},
        #         'di karenakan': {'text': 'dikarenakan', 'rule': 'Penulisan awalan di-'},
        #         'berfikir': {'text': 'berpikir', 'rule': 'Ejaan yang tepat'},
        #         'gud luk': {'text': 'good luck', 'rule': 'Ejaan bahasa Inggris yang benar'},
        #         'bahasa ingris': {'text': 'bahasa Inggris', 'rule': 'Penulisan kata "Inggris" dengan huruf kapital dan ejaan yang benar'},
        #         # Tambahan kata-kata informal dan slang Indonesia
        #         'baeek': {'text': 'baik', 'rule': 'Ejaan yang tepat untuk kata "baik"'},
        #         'okwait': {'text': 'ok tunggu', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'gaskeun': {'text': 'lanjutkan', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'yaudah': {'text': 'ya sudah', 'rule': 'Penulisan kata yang benar'},
        #         'gapapa': {'text': 'tidak apa-apa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'gatau': {'text': 'tidak tahu', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'gajelas': {'text': 'tidak jelas', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'gakbisa': {'text': 'tidak bisa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'makasih': {'text': 'terima kasih', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'mangats': {'text': 'semangat', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'btw': {'text': 'ngomong-ngomong', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'aslinyamah': {'text': 'sebenarnya', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'emg': {'text': 'memang', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'wkwk': {'text': 'haha', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'oot': {'text': 'keluar topik', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'gw': {'text': 'saya', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'lu': {'text': 'anda', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
        #         'asap': {'text': 'secepat mungkin', 'rule': 'Penggunaan kata baku bahasa Indonesia'}
        #     }
        # else:  # English
        #     common_errors = {
        #         'i am': {'text': 'I am', 'rule': 'Capitalization of pronoun "I"'},
        #         'their going': {'text': 'they\'re going', 'rule': 'Use of their vs they\'re'},
        #         'could of': {'text': 'could have', 'rule': 'Use of "could have" instead of "could of"'},
        #         'alot': {'text': 'a lot', 'rule': 'Spelling of "a lot"'},
        #         'i dont': {'text': 'I don\'t', 'rule': 'Contraction and capitalization'},
        #         'gud luk': {'text': 'good luck', 'rule': 'Correct spelling of "good luck"'},
        #         'gud': {'text': 'good', 'rule': 'Correct spelling of "good"'},
        #         'luk': {'text': 'luck', 'rule': 'Correct spelling of "luck"'},
        #         'ur': {'text': 'your', 'rule': 'Correct spelling of "your"'},
        #         'u': {'text': 'you', 'rule': 'Correct spelling of "you"'},
        #         'r': {'text': 'are', 'rule': 'Correct spelling of "are"'},
        #         'y': {'text': 'why', 'rule': 'Correct spelling of "why"'},
        #         'gonna': {'text': 'going to', 'rule': 'Formal form of "gonna"'},
        #         'wanna': {'text': 'want to', 'rule': 'Formal form of "wanna"'},
        #         'gotta': {'text': 'got to', 'rule': 'Formal form of "gotta"'},
        #         'okwait': {'text': 'okay wait', 'rule': 'Use of standard English words'},
        #         'idk': {'text': 'I don\'t know', 'rule': 'Use of standard English words'},
        #         'btw': {'text': 'by the way', 'rule': 'Use of standard English words'},
        #         'lol': {'text': 'laughing out loud', 'rule': 'Use of standard English words'},
        #         'tbh': {'text': 'to be honest', 'rule': 'Use of standard English words'},
        #         'asap': {'text': 'as soon as possible', 'rule': 'Use of standard English words'},
        #         'omg': {'text': 'oh my god', 'rule': 'Use of standard English words'},
        #         'brb': {'text': 'be right back', 'rule': 'Use of standard English words'}
        #     }
    
        # corrected_text = text
        
        # # Prioritaskan pengecekan kasus "di rumah nya" untuk bahasa Indonesia
        # if language == 'id':
        #     # Cek pola khusus "di rumah nya"
        #     if 'di rumah nya' in text.lower():
        #         index = text.lower().find('di rumah nya')
        #         original_text = text[index:index+11]  # Panjang "di rumah nya" adalah 11
        #         fallback_corrections.append({
        #             "start": index,
        #             "end": index + len(original_text),
        #             "text": original_text,
        #             "suggestion": "di rumahnya",
        #             "rule": "Penulisan kata ganti kepunyaan"
        #         })
        #         corrected_text = corrected_text.replace(original_text, "di rumahnya")
            
        #     # Deteksi pola umum kata + spasi + nya
        #     import re
        #     pattern = r'(\w+) nya\b'
        #     for match in re.finditer(pattern, text.lower()):
        #         full_match = match.group(0)
        #         kata_dasar = match.group(1)
                
        #         # Hindari case yang telah ditangani seperti "di rumah nya"
        #         if 'di rumah nya' in text.lower() and 'rumah' in full_match:
        #             continue
                
        #         index = match.start()
        #         # Dapatkan teks asli untuk mempertahankan kapitalisasi
        #         original_text = text[index:index+len(full_match)]
        #         # Buat koreksi
        #         corrected = kata_dasar + "nya"
        #         if original_text[0].isupper():
        #             corrected = corrected[0].upper() + corrected[1:]
                
        #         fallback_corrections.append({
        #             "start": index,
        #             "end": index + len(original_text),
        #             "text": original_text,
        #             "suggestion": corrected,
        #             "rule": "Penulisan kata ganti kepunyaan"
        #         })
        #         corrected_text = corrected_text.replace(original_text, corrected)
        
        # # Lanjutkan dengan koreksi umum lainnya
        # for error, correction in common_errors.items():
        #     if error in text.lower():
        #         # Hindari duplikasi koreksi yang sudah dilakukan
        #         if any(error in corr["text"].lower() for corr in fallback_corrections):
        #             continue
                
        #         index = text.lower().find(error)
        #         fallback_corrections.append({
        #             "start": index,
        #             "end": index + len(error),
        #             "text": text[index:index+len(error)],
        #             "suggestion": correction['text'],
        #             "rule": correction['rule']
        #         })
        #         corrected_text = corrected_text.replace(text[index:index+len(error)], correction['text'])
        
        # # Koreksi tambahan untuk kata-kata informal yang tidak terdaftar
        # if not fallback_corrections:
        #     corrected_text, extra_corrections = correct_informal_words(text, language)
        #     fallback_corrections.extend(extra_corrections)
        
        # # Pastikan teks hasil koreksi fallback bersih dari prefix
        # corrected_text = clean_text_output(corrected_text, language)
        
        # return corrected_text, fallback_corrections

def clean_text_output(text, language='id'):
    """
    Membersihkan output teks dari prefix berulang dan format yang tidak diinginkan
    """
    # Tentukan prefix berdasarkan bahasa
    task_prefix = "grammar: " if language == 'en' else "tata bahasa: "
    
    # Bersihkan prefix di awal
    cleaned_text = text
    while cleaned_text.startswith(task_prefix):
        cleaned_text = cleaned_text[len(task_prefix):].strip()
    
    # Bersihkan prefix di tengah
    if ": " + task_prefix in cleaned_text:
        parts = cleaned_text.split(": " + task_prefix)
        cleaned_text = parts[0]
    
    # Hapus prefix berulang dalam berbagai format
    prefixes = ["tata bahasa:", "grammar:", "koreksi:", "correction:", "bahasa:"]
    for prefix in prefixes:
        if prefix in cleaned_text and cleaned_text.count(prefix) > 1:
            # Ambil hanya bagian pertama sebelum prefix kedua
            parts = cleaned_text.split(prefix, 1)
            if len(parts) > 1:
                cleaned_text = parts[0] + parts[1].split(prefix, 1)[0]
    
    # Deteksi dan hapus pola berulang (3 kata atau lebih yang sama berturut-turut)
    words = cleaned_text.split()
    if len(words) > 3:
        unique_words = []
        prev_word = None
        repetition_count = 0
        max_repetition = 2  # Maksimal 2 kali pengulangan yang diizinkan
        
        for word in words:
            if word == prev_word:
                repetition_count += 1
                if repetition_count < max_repetition:
                    unique_words.append(word)
            else:
                repetition_count = 0
                unique_words.append(word)
                prev_word = word
        
        cleaned_text = ' '.join(unique_words)
    
    # Hapus duplikasi frasa panjang (deteksi perulangan frasa 3+ kata)
    if len(cleaned_text.split()) > 6:  # Minimal ada 6 kata untuk deteksi frasa berulang
        words = cleaned_text.split()
        chunks = [' '.join(words[i:i+3]) for i in range(len(words)-2)]  # Cek frasa 3 kata
        seen_chunks = {}
        duplicate_indexes = set()
        
        for i, chunk in enumerate(chunks):
            if chunk in seen_chunks and i - seen_chunks[chunk] > 2:  # Frasa berulang & tidak berdekatan
                for j in range(i, min(i+3, len(words))):
                    duplicate_indexes.add(j)
            else:
                seen_chunks[chunk] = i
        
        final_words = [word for i, word in enumerate(words) if i not in duplicate_indexes]
        cleaned_text = ' '.join(final_words)
    
    # Bersihkan tanda baca yang tidak perlu di akhir
    cleaned_text = cleaned_text.rstrip('.,:;')
    
    return cleaned_text.strip()

def correct_grammar(text, language='id'):
    """
    Main function to correct grammar using multiple methods
    """
    # Initialize variables for tracking corrections
    all_explanations = []
    best_corrected_text = text
    
    # Periksa dulu dengan rules sederhana (dictionary)
    if language == 'id':
        common_errors = {
            'di rumah nya': {'text': 'di rumahnya', 'rule': 'Penulisan kata ganti kepunyaan'},
            'tidak bisa di terima': {'text': 'tidak bisa diterima', 'rule': 'Penulisan awalan di-'},
            'belajar lah': {'text': 'belajarlah', 'rule': 'Penulisan partikel lah'},
            'di karenakan': {'text': 'dikarenakan', 'rule': 'Penulisan awalan di-'},
            'berfikir': {'text': 'berpikir', 'rule': 'Ejaan yang tepat'},
            'gud luk': {'text': 'good luck', 'rule': 'Ejaan bahasa Inggris yang benar'},
            'bahasa ingris': {'text': 'bahasa Inggris', 'rule': 'Penulisan kata "Inggris" dengan huruf kapital dan ejaan yang benar'},
            'baeek': {'text': 'baik', 'rule': 'Ejaan yang tepat untuk kata "baik"'},
            'okwait': {'text': 'ok tunggu', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gaskeun': {'text': 'lanjutkan', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'yaudah': {'text': 'ya sudah', 'rule': 'Penulisan kata yang benar'},
            'gapapa': {'text': 'tidak apa-apa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gatau': {'text': 'tidak tahu', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gajelas': {'text': 'tidak jelas', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gakbisa': {'text': 'tidak bisa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'makasih': {'text': 'terima kasih', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'mangats': {'text': 'semangat', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'btw': {'text': 'ngomong-ngomong', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'aslinyamah': {'text': 'sebenarnya', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'emg': {'text': 'memang', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'wkwk': {'text': 'haha', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'oot': {'text': 'keluar topik', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gw': {'text': 'saya', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'lu': {'text': 'anda', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'asap': {'text': 'secepat mungkin', 'rule': 'Penggunaan kata baku bahasa Indonesia'}
        }
        
        # Terapkan koreksi langsung berdasarkan kamus
        for error, correction in common_errors.items():
            if error in text.lower():
                index = text.lower().find(error)
                all_explanations.append({
                    "text": text[index:index+len(error)],
                    "suggestion": correction['text'],
                    "rule": correction['rule']
                })
                best_corrected_text = best_corrected_text.replace(text[index:index+len(error)], correction['text'])
        
        # Deteksi pola umum untuk kata + spasi + nya menggunakan regex
        import re
        pattern = r'(\w+) nya\b'
        for match in re.finditer(pattern, text.lower()):
            full_match = match.group(0)
            kata_dasar = match.group(1)
            index = match.start()
            
            # Hindari pencocokan yang sudah ditangani oleh common_errors
            if any(full_match in err for err in common_errors.keys()):
                continue
                
            # Dapatkan teks asli untuk mempertahankan kapitalisasi
            original_text = text[index:index+len(full_match)]
            # Buat koreksi
            corrected = kata_dasar + "nya"
            if original_text[0].isupper():
                corrected = corrected[0].upper() + corrected[1:]
            
            all_explanations.append({
                "text": original_text,
                "suggestion": corrected,
                "rule": "Penulisan kata ganti kepunyaan"
            })
            best_corrected_text = best_corrected_text.replace(original_text, corrected)
    
    # Gunakan kamus kata informal terlebih dahulu (lebih presisi)
    llm_corrected, llm_explanations = simulate_llm_correction(best_corrected_text, language)
    if llm_explanations:
        best_corrected_text = llm_corrected
        
        # Hanya tambahkan penjelasan yang belum ada
        for expl in llm_explanations:
            if not any(expl["text"] == e["text"] for e in all_explanations):
                all_explanations.append(expl)
    
    # Gunakan spaCy untuk analisis lanjutan jika belum ada koreksi
    if len(all_explanations) == 0:
        spacy_issues, _ = analyze_text_with_spacy(text, language)
        all_explanations.extend(spacy_issues)
    
    # Jika belum ada koreksi signifikan, gunakan T5
    if len(all_explanations) < 2:
        try:
            t5_corrected, t5_explanations = correct_with_t5(text, language)
            if t5_explanations and t5_corrected != text:
                # Jika T5 menemukan sesuatu, gunakan hasil T5
                best_corrected_text = t5_corrected
                
                # Tambahkan penjelasan yang belum ada
                for expl in t5_explanations:
                    if not any(expl["text"] == e["text"] for e in all_explanations):
                        all_explanations.append(expl)
        except Exception as e:
            print(f"T5 processing error: {e}")
    
    # Pastikan teks hasil koreksi sudah bersih dari prefix
    best_corrected_text = clean_text_output(best_corrected_text, language)
    
    return best_corrected_text, all_explanations 