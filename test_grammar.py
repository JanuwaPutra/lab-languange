from modules.grammar_correction_t5_spacy import correct_grammar

# Test kasus "waduhh"
print("\n--- TEST KASUS 1: waduhh ---")
hasil, penjelasan = correct_grammar("waduhh", "id")
print(f"Input: waduhh")
print(f"Hasil: {hasil}")
print(f"Penjelasan: {penjelasan}")

# Test kasus dengan teks yang lebih panjang
print("\n--- TEST KASUS 2: teks panjang ---")
text_panjang = "waduhh ini teks saya yg gapapa kalo gak di perhatiin"
hasil, penjelasan = correct_grammar(text_panjang, "id")
print(f"Input: {text_panjang}")
print(f"Hasil: {hasil}")
print(f"Penjelasan: {penjelasan}")

# Test kasus apakabae
print("\n--- TEST KASUS 3: apakabae ---")
hasil, penjelasan = correct_grammar("apakabae", "id")
print(f"Input: apakabae")
print(f"Hasil: {hasil}")
print(f"Penjelasan: {penjelasan}")

# Test kasus kata tidak baku
print("\n--- TEST KASUS 4: kata tidak baku ---")
text_tidak_baku = "gw gatau gmn caranya utk bikin ini skrg jd gw trs gini aja"
hasil, penjelasan = correct_grammar(text_tidak_baku, "id")
print(f"Input: {text_tidak_baku}")
print(f"Hasil: {hasil}")
print(f"Penjelasan: {penjelasan}") 