import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer, MT5ForConditionalGeneration, MT5Tokenizer
import os
import re
from dotenv import load_dotenv

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
    
    # Load mT5 model for multilingual grammar correction - gunakan small (ukuran terkecil)
    model_name = "google/mt5-small"  # Multilingual T5 model
    print(f"Loading multilingual T5 model: {model_name}")
    tokenizer_mt5 = MT5Tokenizer.from_pretrained(model_name)
    model_mt5 = MT5ForConditionalGeneration.from_pretrained(model_name)
    
    # Also load T5 model for English-specific grammar correction - gunakan small (ukuran terkecil)
    en_model_name = "t5-small"
    print(f"Loading English T5 model: {en_model_name}")
    tokenizer_t5 = T5Tokenizer.from_pretrained(en_model_name)
    model_t5 = T5ForConditionalGeneration.from_pretrained(en_model_name)
    
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
    
    # Specific rules for Indonesian
    if language == 'id':
        # Check for "di" and "ke" prefix issues
        for match in re.finditer(r'\b(di|ke) ([a-zA-Z])', text):
            prefix, word = match.groups()
            if not re.match(r'\b(di|ke)[a-zA-Z]', word):  # Should be merged
                issues.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(),
                    "suggestion": f"{prefix}{word}",
                    "rule": f"Penulisan kata depan '{prefix}' dengan kata setelahnya"
                })
                
        # Check for "-nya" suffix issues
        for match in re.finditer(r'\b([a-zA-Z]+) nya\b', text):
            word = match.group(1)
            issues.append({
                "start": match.start(),
                "end": match.end(),
                "text": f"{word} nya",
                "suggestion": f"{word}nya",
                "rule": "Penulisan akhiran '-nya'"
            })
    
    # Check for English common errors
    if language == 'en':
        # Check "your" vs "you're"
        for match in re.finditer(r'\byour\b(?!\s+(own|self))', text):
            if doc[match.start():match.end()].text == "your":
                # Check context to see if "you're" would be more appropriate
                is_before_verb = False
                for token in doc[match.end():]:
                    if token.pos_ == "VERB":
                        is_before_verb = True
                        break
                    if token.pos_ in ["PUNCT", "CCONJ"]:
                        break
                
                if is_before_verb:
                    issues.append({
                        "start": match.start(),
                        "end": match.end(),
                        "text": "your",
                        "suggestion": "you're",
                        "rule": "Penggunaan 'your' vs 'you're'"
                    })
                
        # Check "their" vs "they're" vs "there"
        for match in re.finditer(r'\b(their|there|they\'re)\b', text):
            word = match.group(1)
            token_span = doc[match.start():match.end()]
            
            # Simple heuristic for checking usage
            next_token_idx = match.end() + 1
            if next_token_idx < len(doc) and doc[next_token_idx].pos_ == "VERB":
                if word != "they're":
                    issues.append({
                        "start": match.start(),
                        "end": match.end(),
                        "text": word,
                        "suggestion": "they're",
                        "rule": "Penggunaan 'their' vs 'they're' vs 'there'"
                    })
            elif word == "they're" and next_token_idx < len(doc) and doc[next_token_idx].pos_ == "NOUN":
                issues.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": word,
                    "suggestion": "their",
                    "rule": "Penggunaan 'their' vs 'they're' vs 'there'"
                })
    
    return issues, doc.text

def correct_with_t5(text, language='id'):
    """
    Use T5 model to correct grammar based on language
    """
    if not models_loaded:
        return text, "Model tidak dapat dimuat. Periksa instalasi."
    
    try:
        # Use the appropriate model and tokenizer based on language
        if language == 'en':
            model = model_t5
            tokenizer = tokenizer_t5
            task_prefix = "correct grammar: "
        else:
            model = model_mt5
            tokenizer = tokenizer_mt5
            task_prefix = "perbaiki tata bahasa: "
        
        # Kasus khusus - dictionary kata yang sering salah tulis
        common_misspellings = {
            'waduhh': 'waduh',
            'aduhh': 'aduh',
            'gimana': 'bagaimana',
            'gak': 'tidak',
            'ngga': 'tidak',
            'nggak': 'tidak',
            'deh': '',
            'aja': 'saja',
            'banget': 'sekali',
            'kyk': 'seperti',
            'kayak': 'seperti',
            'gitu': 'begitu',
            'gini': 'begini',
            'udah': 'sudah',
            'udeh': 'sudah',
            'apakabae': 'apakah',
            'trs': 'terus',
        }
        
        # Cek dulu apakah ada kata dalam common_misspellings
        words = text.split()
        corrected_words = []
        made_changes = False
        
        for word in words:
            word_lower = word.lower()
            if word_lower in common_misspellings:
                replacement = common_misspellings[word_lower]
                if replacement:  # Jika replacement bukan string kosong
                    corrected_words.append(replacement)
                made_changes = True
            else:
                corrected_words.append(word)
        
        # Jika ada perubahan dari kamus, gunakan hasil itu
        if made_changes:
            corrected_text = ' '.join(corrected_words)
            return corrected_text, [{
                "text": text,
                "suggestion": corrected_text,
                "rule": "Koreksi kata tidak baku"
            }]
        
        # Jika teks terlalu panjang, T5 bisa bermasalah, jadi pecah menjadi kalimat
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 1 and len(text) > 100:
            # Proses per kalimat
            corrected_sentences = []
            for sent in sentences:
                # Panggil rekursif untuk setiap kalimat
                sent_corrected, _ = correct_with_t5(sent, language)
                corrected_sentences.append(sent_corrected)
            
            corrected_text = ' '.join(corrected_sentences)
            return corrected_text, [{
                "text": text,
                "suggestion": corrected_text,
                "rule": "Koreksi tata bahasa per kalimat"
            }]
        
        # Hanya gunakan T5 untuk teks di bawah 200 karakter untuk menghindari masalah
        if len(text) > 200:
            return text, []
            
        # Format input for T5/mT5
        input_text = task_prefix + text
        
        # Tokenize and generate correction
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=128, truncation=True)
        
        # Parameter generasi yang lebih ringan
        outputs = model.generate(
            input_ids, 
            max_length=128,
            num_beams=2,
            length_penalty=1.0,
            early_stopping=True
        )
        
        corrected_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Hapus token special dan bersihkan output
        corrected_text = re.sub(r'<extra_id_\d+>', '', corrected_text)
        
        # Jika model mengembalikan prefix, hapus
        if corrected_text.startswith(task_prefix):
            corrected_text = corrected_text[len(task_prefix):].strip()
        
        # Validasi output - jika terlalu berbeda, kembalikan teks asli
        if len(corrected_text) < len(text) * 0.5 or corrected_text == text or not corrected_text:
            return text, []
            
        return corrected_text, [{
            "text": text,
            "suggestion": corrected_text,
            "rule": f"Koreksi model {'T5' if language == 'en' else 'mT5'}"
        }]
    except Exception as e:
        print(f"Error in T5 correction: {e}")
        return text, []

def correct_common_errors(text, language='id'):
    """
    Apply rule-based corrections for common errors
    """
    corrections = []
    
    if language == 'id':
        common_errors = {
            # Imbuhan dan Kata Depan
            'di rumah nya': {'text': 'di rumahnya', 'rule': 'Penulisan kata ganti kepunyaan'},
            'tidak bisa di terima': {'text': 'tidak bisa diterima', 'rule': 'Penulisan awalan di-'},
            'belajar lah': {'text': 'belajarlah', 'rule': 'Penulisan partikel lah'},
            'di karenakan': {'text': 'dikarenakan', 'rule': 'Penulisan awalan di-'},
            'ke tahui': {'text': 'ketahui', 'rule': 'Penulisan awalan ke-'},
            'pe nyanyi': {'text': 'penyanyi', 'rule': 'Penulisan awalan pe-'},
            'se orang': {'text': 'seorang', 'rule': 'Penulisan awalan se-'},
            
            # Ejaan yang Benar
            'berfikir': {'text': 'berpikir', 'rule': 'Ejaan yang tepat'},
            'ijin': {'text': 'izin', 'rule': 'Ejaan yang tepat'},
            'aktifitas': {'text': 'aktivitas', 'rule': 'Ejaan yang tepat'},
            'praktek': {'text': 'praktik', 'rule': 'Ejaan yang tepat'},
            'negri': {'text': 'negeri', 'rule': 'Ejaan yang tepat'},
            'nasehat': {'text': 'nasihat', 'rule': 'Ejaan yang tepat'},
            'apotik': {'text': 'apotek', 'rule': 'Ejaan yang tepat'},
            'sistim': {'text': 'sistem', 'rule': 'Ejaan yang tepat'},
            'hakekat': {'text': 'hakikat', 'rule': 'Ejaan yang tepat'},
            'insyaf': {'text': 'insaf', 'rule': 'Ejaan yang tepat'},
            'syarat': {'text': 'syarat', 'rule': 'Ejaan yang tepat'},
            'jaman': {'text': 'zaman', 'rule': 'Ejaan yang tepat'},
            'obyek': {'text': 'objek', 'rule': 'Ejaan yang tepat'},
            
            # Kata-kata Tidak Baku & Slang
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
            'asap': {'text': 'secepat mungkin', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'otw': {'text': 'sedang dalam perjalanan', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'lol': {'text': 'tertawa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gpp': {'text': 'tidak apa-apa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'bgt': {'text': 'sekali', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'yg': {'text': 'yang', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'dgn': {'text': 'dengan', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'utk': {'text': 'untuk', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'tdk': {'text': 'tidak', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'sdh': {'text': 'sudah', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'blm': {'text': 'belum', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'kyk': {'text': 'seperti', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gini': {'text': 'begini', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'gitu': {'text': 'begitu', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'skrg': {'text': 'sekarang', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'bbrp': {'text': 'beberapa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'bs': {'text': 'bisa', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'dpt': {'text': 'dapat', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'tp': {'text': 'tetapi', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'bnr': {'text': 'benar', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'krn': {'text': 'karena', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'dr': {'text': 'dari', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'waduhh': {'text': 'waduh', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'duhh': {'text': 'duh', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'aduhh': {'text': 'aduh', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'yaudah': {'text': 'ya sudah', 'rule': 'Penulisan kata yang benar'},
            'gmn': {'text': 'bagaimana', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'sy': {'text': 'saya', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'trs': {'text': 'terus', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'udah': {'text': 'sudah', 'rule': 'Penggunaan kata baku bahasa Indonesia'},
            'apakabae': {'text': 'apakah', 'rule': 'Penggunaan kata baku bahasa Indonesia'}
        }
    else:  # English
        common_errors = {
            'i am': {'text': 'I am', 'rule': 'Capitalization of pronoun "I"'},
            'their going': {'text': 'they\'re going', 'rule': 'Use of their vs they\'re'},
            'could of': {'text': 'could have', 'rule': 'Use of "could have" instead of "could of"'},
            'alot': {'text': 'a lot', 'rule': 'Spelling of "a lot"'},
            'i dont': {'text': 'I don\'t', 'rule': 'Contraction and capitalization'},
            'gud luk': {'text': 'good luck', 'rule': 'Correct spelling of "good luck"'},
            'gud': {'text': 'good', 'rule': 'Correct spelling of "good"'},
            'luk': {'text': 'luck', 'rule': 'Correct spelling of "luck"'},
            'ur': {'text': 'your', 'rule': 'Correct spelling of "your"'},
            'u': {'text': 'you', 'rule': 'Correct spelling of "you"'},
            'r': {'text': 'are', 'rule': 'Correct spelling of "are"'},
            'y': {'text': 'why', 'rule': 'Correct spelling of "why"'},
            'gonna': {'text': 'going to', 'rule': 'Formal form of "gonna"'},
            'wanna': {'text': 'want to', 'rule': 'Formal form of "wanna"'},
            'gotta': {'text': 'got to', 'rule': 'Formal form of "gotta"'},
            'okwait': {'text': 'okay wait', 'rule': 'Use of standard English words'},
            'idk': {'text': 'I don\'t know', 'rule': 'Use of standard English words'},
            'btw': {'text': 'by the way', 'rule': 'Use of standard English words'},
            'lol': {'text': 'laughing out loud', 'rule': 'Use of standard English words'},
            'tbh': {'text': 'to be honest', 'rule': 'Use of standard English words'},
            'asap': {'text': 'as soon as possible', 'rule': 'Use of standard English words'},
            'omg': {'text': 'oh my god', 'rule': 'Use of standard English words'},
            'brb': {'text': 'be right back', 'rule': 'Use of standard English words'}
        }

    corrected_text = text
    
    for error, correction in common_errors.items():
        if error in text.lower():
            index = text.lower().find(error)
            corrections.append({
                "start": index,
                "end": index + len(error),
                "text": text[index:index+len(error)],
                "suggestion": correction['text'],
                "rule": correction['rule']
            })
            corrected_text = corrected_text.replace(text[index:index+len(error)], correction['text'])
    
    return corrected_text, corrections

def correct_grammar(text, language='id'):
    """
    Main function to correct grammar using multiple methods with lightweight T5
    """
    # Initialize variables for tracking corrections
    all_explanations = []
    best_corrected_text = text
    
    # 1. Apply manual dictionary corrections first (paling cepat dan akurat)
    rule_corrected, rule_explanations = correct_common_errors(text, language)
    if rule_explanations:
        best_corrected_text = rule_corrected
        all_explanations.extend(rule_explanations)
    
    # 2. Coba T5/mT5 model untuk kata-kata tidak baku & singkatan umum
    # Ini akan menggunakan kamus kata yang dibuat khusus di dalam fungsi correct_with_t5
    try:
        t5_corrected, t5_explanations = correct_with_t5(best_corrected_text, language)
        
        # Gunakan hasil T5 hanya jika valid
        if t5_explanations and t5_corrected and t5_corrected != best_corrected_text:
            best_corrected_text = t5_corrected
            all_explanations.extend(t5_explanations)
    except Exception as e:
        print(f"T5 processing error: {e}")
    
    # 3. Use spaCy untuk analisis struktur kalimat (grammar rules)
    spacy_issues, _ = analyze_text_with_spacy(best_corrected_text, language)
    if spacy_issues:
        # Apply spaCy-detected corrections
        corrected = best_corrected_text
        for issue in spacy_issues:
            if 'text' in issue and 'suggestion' in issue:
                corrected = corrected.replace(issue['text'], issue['suggestion'])
        
        if corrected != best_corrected_text:
            best_corrected_text = corrected
            all_explanations.extend(spacy_issues)
    
    return best_corrected_text, all_explanations