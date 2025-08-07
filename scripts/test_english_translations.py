#!/usr/bin/env python3

import argostranslate.translate

def test_english_translations():
    """Test English translations (bidirectional when available, otherwise single direction)."""
    languages = argostranslate.translate.get_installed_languages()
    print(f"Using {len(languages)} already-loaded languages")
    
    # Find English language
    english = next((lang for lang in languages if lang.code == "en"), None)
    if not english:
        print("English language not available")
        return
        
    # Get English translation pairs (bidirectional and single-direction)
    translation_pairs = {}
    
    # Add EN->X translations
    for translation in english.translations_from:
        if translation.to_lang.code == "en":  # Skip English->English
            continue
        lang_code = translation.to_lang.code
        translation_pairs[lang_code] = {
            'lang_name': translation.to_lang.name,
            'en_to_x': translation,
            'x_to_en': None
        }
    
    # Add X->EN translations and mark bidirectional pairs
    bidirectional_count = 0
    for lang in languages:
        if lang.code != "en":
            reverse_translation = lang.get_translation(english)
            if reverse_translation:
                lang_code = lang.code
                if lang_code in translation_pairs:
                    # Complete bidirectional pair
                    translation_pairs[lang_code]['x_to_en'] = reverse_translation
                    bidirectional_count += 1
                else:
                    # Only X->EN translation available
                    translation_pairs[lang_code] = {
                        'lang_name': lang.name,
                        'en_to_x': None,
                        'x_to_en': reverse_translation
                    }
    
    print(f"Found {len(translation_pairs)} languages with English translation pairs")
    print(f"Bidirectional pairs: {bidirectional_count}, Single-direction: {len(translation_pairs) - bidirectional_count}")
    
    test_phrases = {
        # Basic phrases
        "simple_hello": "Hello world",
        "simple_greeting": "Good morning",
        
        # SBD stress test phrases - multiple sentences
        "two_sentences": "Hello world. How are you today?",
        "exclamation_period": "Good morning! Nice to see you.",
        "question_statement": "What time is it? It is three thirty.",
        "abbreviations": "Dr. Smith went to the U.S.A. yesterday.",
        "quoted_speech": "He said, 'Hello there.' Then he left.",
        
        # Longer coherent text
        "quick_brown_fox": "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
        "longer_paragraph": "Once upon a time, there was a small village. The people were very friendly. They welcomed all visitors with open arms. Everyone lived in harmony together.",
        "complex_punctuation": "What a beautiful day! Isn't it wonderful? Yes, I think so too.",
    }
    successful_languages = []
    failed_languages = []
    
    for lang_code, data in translation_pairs.items():
        print(f"\n=== Testing {lang_code} ({data['lang_name']}) ===")
        
        en_to_x_translation = data['en_to_x']
        x_to_en_translation = data['x_to_en']
        
        # Determine test type
        if en_to_x_translation and x_to_en_translation:
            test_type = "bidirectional"
        elif en_to_x_translation:
            test_type = "EN->X only"
        else:
            test_type = "X->EN only"
        
        print(f"  Test type: {test_type}")
        lang_success = True
        
        for test_name, phrase in test_phrases.items():
            try:
                print(f"  [{test_name}]")
                if test_type == "bidirectional":
                    # Test full roundtrip
                    forward_result = en_to_x_translation.translate(phrase)
                    print(f"    EN->({lang_code}): '{phrase}' -> '{forward_result}'")
                    
                    backward_result = x_to_en_translation.translate(forward_result)
                    print(f"    ({lang_code})->EN: '{forward_result}' -> '{backward_result}'")
                    
                    # Smoke test assertions
                    if not (forward_result and len(forward_result.strip()) > 0):
                        raise Exception(f"Forward translation failed for {lang_code}")
                    if not (backward_result and len(backward_result.strip()) > 0):
                        raise Exception(f"Backward translation failed for {lang_code}")
                    
                    print(f"    ✓ Roundtrip successful")
                    
                elif test_type == "EN->X only":
                    # Test only EN->X translation
                    forward_result = en_to_x_translation.translate(phrase)
                    print(f"    EN->({lang_code}): '{phrase}' -> '{forward_result}'")
                    
                    if not (forward_result and len(forward_result.strip()) > 0):
                        raise Exception(f"Forward translation failed for {lang_code}")
                    
                    print(f"    ✓ One-way translation successful")
                    
                else:  # X->EN only
                    # For X->EN only, use the phrase as if it's in the source language
                    backward_result = x_to_en_translation.translate(phrase)
                    print(f"    ({lang_code})->EN: '{phrase}' -> '{backward_result}'")
                    
                    if not (backward_result and len(backward_result.strip()) > 0):
                        raise Exception(f"Backward translation failed for {lang_code}")
                    
                    print(f"    ✓ One-way translation successful")
                
            except Exception as e:
                print(f"    ✗ Translation failed for {lang_code} with test '{test_name}': {e}")
                lang_success = False
                break  # Skip remaining phrases for this language
                
        if lang_success:
            successful_languages.append(lang_code)
            print(f"  ✓ Language {lang_code} completed all tests")
        else:
            failed_languages.append(lang_code)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Successful languages ({len(successful_languages)}): {successful_languages}")
    print(f"Failed languages ({len(failed_languages)}): {failed_languages}")
    print(f"Success rate: {len(successful_languages)}/{len(translation_pairs)} ({len(successful_languages)/len(translation_pairs)*100:.1f}%)")

if __name__ == "__main__":
    test_english_translations()