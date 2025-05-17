import speech_recognition as sr
import os
import tempfile
import jiwer
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def recognize_speech_from_file(audio_file, language='id'):
    """
    Recognize speech from uploaded audio file
    """
    recognizer = sr.Recognizer()
    
    # Save the audio file to a temporary file if it's a file object
    if hasattr(audio_file, 'read'):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_filename = temp_file.name
            audio_file.save(temp_filename)
    else:
        # If it's already a filename
        temp_filename = audio_file
    
    try:
        with sr.AudioFile(temp_filename) as source:
            audio_data = recognizer.record(source)
            
            # Determine language code for speech recognition
            lang_code = "id-ID" if language == "id" else "en-US"
            
            # Use Google's speech recognition service
            text = recognizer.recognize_google(audio_data, language=lang_code)
            return text
    except sr.UnknownValueError:
        return "Tidak dapat mengenali audio"
    except sr.RequestError:
        return "Layanan speech recognition tidak tersedia"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Clean up the temporary file if we created one
        if hasattr(audio_file, 'read') and os.path.exists(temp_filename):
            os.remove(temp_filename)

def calculate_pronunciation_accuracy(recognized_text, reference_text):
    """
    Calculate how accurately the recognized speech matches the reference text
    """
    # Remove capitalization and punctuation for comparison
    recognized_clean = ''.join(e.lower() for e in recognized_text if e.isalnum() or e.isspace())
    reference_clean = ''.join(e.lower() for e in reference_text if e.isalnum() or e.isspace())
    
    # Calculate Word Error Rate (WER)
    wer = jiwer.wer(reference_clean, recognized_clean)
    
    # Convert WER to accuracy percentage (100% - WER%)
    accuracy = max(0, 100 - wer * 100)
    
    return round(accuracy, 1)

def generate_pronunciation_feedback(recognized_text, reference_text, accuracy, language='id'):
    """
    Generate feedback based on pronunciation accuracy
    """
    feedback = ""
    
    if accuracy > 90:
        feedback = "Sangat bagus! Pengucapan Anda sangat jelas." if language == 'id' else "Excellent! Your pronunciation is very clear."
    elif accuracy > 75:
        feedback = "Bagus! Pengucapan Anda cukup jelas." if language == 'id' else "Good! Your pronunciation is fairly clear."
    elif accuracy > 50:
        feedback = "Cukup baik. Perhatikan pengucapan beberapa kata." if language == 'id' else "Fairly good. Pay attention to the pronunciation of some words."
    else:
        feedback = "Perlu latihan lebih. Cobalah bicara lebih jelas dan perlahan." if language == 'id' else "Needs more practice. Try speaking more clearly and slowly."
    
    # Identify specific words that might be mispronounced
    if accuracy < 90:
        recognized_words = recognized_text.lower().split()
        reference_words = reference_text.lower().split()
        
        # Find words that don't match
        if len(recognized_words) > 0 and len(reference_words) > 0:
            # Simple word comparison (in a real implementation, you'd use more sophisticated alignment)
            mismatched_words = []
            
            min_len = min(len(recognized_words), len(reference_words))
            for i in range(min_len):
                if recognized_words[i] != reference_words[i]:
                    mismatched_words.append(reference_words[i])
            
            if mismatched_words:
                word_list = ", ".join(mismatched_words[:3])  # Limit to first 3 words
                if language == 'id':
                    feedback += f" Perhatikan pengucapan kata-kata berikut: {word_list}."
                else:
                    feedback += f" Pay attention to the pronunciation of these words: {word_list}."
    
    return feedback

def recognize_speech(audio_file, reference_text='', language='id'):
    """
    Main function to handle speech recognition and evaluation
    """
    # Recognize speech from the audio file
    recognized_text = recognize_speech_from_file(audio_file, language)
    
    # Calculate accuracy if reference text was provided
    if reference_text:
        accuracy = calculate_pronunciation_accuracy(recognized_text, reference_text)
        feedback = generate_pronunciation_feedback(recognized_text, reference_text, accuracy, language)
    else:
        # If no reference text, just return the recognized text without evaluation
        accuracy = None
        feedback = "Tidak ada teks referensi untuk evaluasi" if language == 'id' else "No reference text for evaluation"
    
    return recognized_text, accuracy, feedback 