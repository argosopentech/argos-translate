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
    
    test_phrases = ["Hello world", "Good morning"]
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
        
        for phrase in test_phrases:
            try:
                if test_type == "bidirectional":
                    # Test full roundtrip
                    forward_result = en_to_x_translation.translate(phrase)
                    print(f"  EN->({lang_code}): '{phrase}' -> '{forward_result}'")
                    
                    backward_result = x_to_en_translation.translate(forward_result)
                    print(f"  ({lang_code})->EN: '{forward_result}' -> '{backward_result}'")
                    
                    # Smoke test assertions
                    if not (forward_result and len(forward_result.strip()) > 0):
                        raise Exception(f"Forward translation failed for {lang_code}")
                    if not (backward_result and len(backward_result.strip()) > 0):
                        raise Exception(f"Backward translation failed for {lang_code}")
                    
                    print(f"  ✓ Roundtrip successful: '{phrase}' -> '{forward_result}' -> '{backward_result}'")
                    
                elif test_type == "EN->X only":
                    # Test only EN->X translation
                    forward_result = en_to_x_translation.translate(phrase)
                    print(f"  EN->({lang_code}): '{phrase}' -> '{forward_result}'")
                    
                    if not (forward_result and len(forward_result.strip()) > 0):
                        raise Exception(f"Forward translation failed for {lang_code}")
                    
                    print(f"  ✓ One-way translation successful: '{phrase}' -> '{forward_result}'")
                    
                else:  # X->EN only
                    # Test only X->EN translation (use a simple foreign phrase)
                    test_input = "Hello"  # Simple test since we don't have EN->X
                    backward_result = x_to_en_translation.translate(test_input)
                    print(f"  ({lang_code})->EN: '{test_input}' -> '{backward_result}'")
                    
                    if not (backward_result and len(backward_result.strip()) > 0):
                        raise Exception(f"Backward translation failed for {lang_code}")
                    
                    print(f"  ✓ One-way translation successful: '{test_input}' -> '{backward_result}'")
                
            except Exception as e:
                print(f"  ✗ Translation failed for {lang_code} with phrase '{phrase}': {e}")
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