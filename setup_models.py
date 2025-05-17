import os
import subprocess
import sys
import time

def check_model_installed(model_name):
    """Check if a spaCy model is already installed"""
    try:
        __import__(model_name)
        return True
    except ImportError:
        return False

def create_token_manually():
    """Guide user to create and input token manually"""
    print("\n=== INSTRUKSI LOGIN HUGGING FACE ===")
    print("Karena terdapat masalah dengan login otomatis, ikuti langkah-langkah berikut:")
    print("1. Buka website: https://huggingface.co/settings/tokens")
    print("2. Login atau daftar di Hugging Face jika Anda belum memiliki akun")
    print("3. Klik 'New Token', beri nama (misal: 'lab-bahasa-token')")
    print("4. Pilih role 'read'")
    print("5. Klik 'Generate a token'")
    print("6. Salin token yang dihasilkan")
    
    # Tawarkan token default yang sudah disediakan
    default_token = "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"
    print(f"\nToken default tersedia. Tekan Enter untuk menggunakan token default ini.")
    token = input("\nMasukkan token Hugging Face Anda (atau tekan Enter untuk menggunakan token default): ")
    
    if token.strip() == "":
        token = default_token
        print("Menggunakan token default.")
    
    # Save token to huggingface-cli credentials
    try:
        token_path = os.path.expanduser("~/.huggingface/token")
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(token)
        print("Token berhasil disimpan!")
        return token
    except Exception as e:
        print(f"Gagal menyimpan token: {e}")
        return None

def main():
    print("=== Setup untuk Lab Bahasa AI ===")
    print("Script ini akan menginstal model-model bahasa yang diperlukan")
    print("Proses ini mungkin memerlukan waktu beberapa menit tergantung kecepatan internet")
    
    # Menginstall model bahasa Inggris
    en_model = "en_core_web_sm"
    if check_model_installed(en_model):
        print(f"Model {en_model} sudah terinstal.")
    else:
        print(f"Menginstall model bahasa Inggris ({en_model})...")
        subprocess.run([sys.executable, "-m", "spacy", "download", en_model])
    
    # Menginstall model bahasa Indonesia
    id_models = ["id_core_news_sm", "id_core_news_md"]
    
    print("\nModel bahasa Indonesia:")
    print("1. id_core_news_sm (lebih kecil, lebih cepat, tidak memerlukan login)")
    print("2. id_core_news_md (lebih besar, lebih akurat, menggunakan token Hugging Face yang sudah tersedia)")
    print("3. Lewati instalasi model bahasa Indonesia")
    
    choice = input("Pilih model yang ingin diinstal [1-3]: ")
    
    if choice == "1":
        model = id_models[0]
        print(f"Menginstall model {model}...")
        # Coba metode 1: Instalasi melalui spacy
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", model])
            print(f"Model {model} berhasil diinstal!")
        except Exception as e:
            print(f"Error (metode 1): {e}")
            # Coba metode 2: Instalasi langsung dari URL
            print("Coba menginstal dengan metode 2...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "--no-deps", "--force-reinstall",
                    "https://github.com/explosion/spacy-models/releases/download/id_core_news_sm-0.0.1/id_core_news_sm-0.0.1-py3-none-any.whl"
                ])
                print(f"Model {model} berhasil diinstal dengan metode 2!")
            except Exception as e2:
                print(f"Error (metode 2): {e2}")
                print("Tidak dapat menginstal model. Program akan menggunakan model bahasa Inggris sebagai fallback.")
    
    elif choice == "2":
        model = id_models[1]
        print(f"Menginstall model {model}...")
        print("Model ini memerlukan token Hugging Face.")
        
        # Instalasi huggingface_hub
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "huggingface_hub"])
        
        # Set token default
        default_token = "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"
        print("\nMenggunakan token default yang sudah tersedia...")
        
        # Simpan token default ke file
        try:
            token_path = os.path.expanduser("~/.huggingface/token")
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, "w") as f:
                f.write(default_token)
            print("Token berhasil disimpan!")
            token = default_token
        except Exception as e:
            print(f"Gagal menyimpan token default: {e}")
            # Jika gagal, coba mendapatkan token secara manual
            token = create_token_manually()
        
        if token:
            print("\nMencoba menginstal model dengan token...")
            try:
                # Gunakan token dalam variabel lingkungan
                env = os.environ.copy()
                env["HUGGING_FACE_HUB_TOKEN"] = token
                
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "--no-deps", "--force-reinstall",
                    "https://huggingface.co/spacy/id_core_news_md/resolve/main/id_core_news_md-0.0.1-py3-none-any.whl"
                ], env=env)
                print(f"Model {model} berhasil diinstal!")
            except Exception as e:
                print(f"Error: {e}")
                print("\nInstalasi gagal. Mencoba metode alternatif...")
                
                # Coba alternatif - gunakan model kecil sebagai fallback
                try:
                    subprocess.run([sys.executable, "-m", "spacy", "download", id_models[0]])
                    print(f"Model {id_models[0]} berhasil diinstal sebagai alternatif.")
                except Exception as e2:
                    print(f"Error instalasi alternatif: {e2}")
                    print("Instalasi model alternatif juga gagal.")
        else:
            print("Token tidak disediakan. Melewati instalasi model yang memerlukan otentikasi.")
            
            # Coba model kecil
            print("Mencoba menginstal model kecil sebagai alternatif...")
            try:
                subprocess.run([sys.executable, "-m", "spacy", "download", id_models[0]])
                print(f"Model {id_models[0]} berhasil diinstal sebagai alternatif.")
            except:
                print("Instalasi model alternatif juga gagal.")
    else:
        print("Melewati instalasi model bahasa Indonesia.")
        print("Catatan: Program akan menggunakan model bahasa Inggris sebagai fallback.")
    
    # Menginstall transformers model (akan didownload otomatis saat pertama kali digunakan)
    print("\nModel T5 akan didownload otomatis saat aplikasi pertama kali dijalankan.")
    print("Ini mungkin memerlukan waktu beberapa menit pada startup pertama.")
    
    print("\nSetup selesai!")
    print("\nTekan Enter untuk keluar...")
    input()

if __name__ == "__main__":
    main() 