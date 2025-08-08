import pytest
import time
from argostranslate import translate


TEST_PHRASES = {
    "simple": "Hello world",
    "sentence": "The quick brown fox jumps over the lazy dog.",
    "paragraph": "Once upon a time, there was a small village. The people were very friendly. They welcomed all visitors with open arms.",
    "long_paragraph": "In the heart of a bustling city, there stood an old library that had witnessed countless stories unfold within its walls. Generations of readers had walked through its doors, seeking knowledge, adventure, and solace among the countless books that lined its shelves. The librarian, Mrs. Henderson, had worked there for over thirty years and knew every corner of the building by heart. She would often tell visitors about the library's rich history, how it survived two world wars, and how it continued to serve as a beacon of learning for the community. During quiet afternoons, sunlight would stream through the tall windows, casting golden rays across the reading tables where students studied and elderly patrons enjoyed their favorite novels. The library was more than just a building filled with books; it was a sanctuary where minds could wander freely and imaginations could soar to distant lands.",
}


@pytest.fixture(scope="session")
def all_translation_packages():
    """Get all installed translation packages."""
    import argostranslate.package as package
    
    installed_packages = package.get_installed_packages()
    languages = translate.get_installed_languages()
    lang_lookup = {lang.code: lang for lang in languages}
    
    pairs = []
    for pkg in installed_packages:
        from_lang = lang_lookup.get(pkg.from_code)
        to_lang = lang_lookup.get(pkg.to_code)
        
        if from_lang and to_lang:
            translation_obj = from_lang.get_translation(to_lang)
            if translation_obj:
                pairs.append({
                    'from_code': pkg.from_code,
                    'from_name': pkg.from_name,
                    'to_code': pkg.to_code,
                    'to_name': pkg.to_name,
                    'package': pkg,
                    'translation': translation_obj
                })
    
    print(f"\n📋 Found {len(pairs)} translation packages")
    return pairs


@pytest.fixture(scope="session") 
def english_to_x_pairs(all_translation_packages):
    """Get English→X pairs where X→English also exists."""
    available_pairs = {(pkg['from_code'], pkg['to_code']) for pkg in all_translation_packages}
    
    english_to_x = []
    for pkg in all_translation_packages:
        from_code, to_code = pkg['from_code'], pkg['to_code']
        
        # English to X (where X to English also exists)
        if from_code == 'en' and (to_code, 'en') in available_pairs:
            english_to_x.append(pkg)
    
    # Sort by target language code
    english_to_x.sort(key=lambda x: x['to_code'])
    
    print(f"📊 Found {len(english_to_x)} English→X pairs with reverse")
    return english_to_x




@pytest.fixture(scope="session")
def directional_only_pairs(all_translation_packages):
    """Get pairs that only go one direction."""
    available_pairs = {(pkg['from_code'], pkg['to_code']) for pkg in all_translation_packages}
    
    directional = []
    for pkg in all_translation_packages:
        from_code, to_code = pkg['from_code'], pkg['to_code']
        
        # English pairs with no reverse
        if from_code == 'en' and (to_code, 'en') not in available_pairs:
            directional.append(pkg)
        elif to_code == 'en' and ('en', from_code) not in available_pairs:
            directional.append(pkg)
    
    print(f"📊 Found {len(directional)} directional-only English pairs")
    return directional


@pytest.fixture(scope="session") 
def non_english_pairs(all_translation_packages):
    """Get all non-English translation pairs."""
    non_english = [pkg for pkg in all_translation_packages 
                  if pkg['from_code'] != 'en' and pkg['to_code'] != 'en']
    
    print(f"📊 Found {len(non_english)} non-English pairs")
    return non_english


class TestSystemStatus:
    """Basic system health checks."""
    
    def test_languages_available(self):
        """Check that languages are installed."""
        languages = translate.get_installed_languages()
        if len(languages) == 0:
            pytest.skip("No languages installed")
        print(f"✓ {len(languages)} languages available")
    
    def test_translation_packages_exist(self, all_translation_packages):
        """Check that translation packages exist."""
        if len(all_translation_packages) == 0:
            pytest.skip("No translation packages found")
        print(f"✓ {len(all_translation_packages)} translation packages available")


class TestEnglishToX:
    """Test English→X translations (where X→English also exists)."""
    
    def test_english_to_x_basic(self, english_to_x_pairs):
        """Test English→X translations."""
        if not english_to_x_pairs:
            pytest.skip("No English→X pairs available")
            
        test_phrase = "Hello world"
        failures = []
        
        for i, pair in enumerate(english_to_x_pairs, 1):
            from_name = pair['from_name']
            to_name = pair['to_name']
            translation = pair['translation']
            
            print(f"\n[{i}/{len(english_to_x_pairs)}] {from_name} → {to_name}")
            
            try:
                result = translation.translate(test_phrase)
                assert result and len(result.strip()) > 0, "Empty translation result"
                print(f"  ✓ '{test_phrase}' → '{result}'")
            except Exception as e:
                error_msg = f"{from_name} → {to_name}: {str(e)}"
                failures.append(error_msg)
                print(f"  ✗ FAILED: {e}")
        
        if failures:
            pytest.fail(f"{len(failures)} English→X pairs failed:\n" + "\n".join(failures))
        
        print(f"\n🎉 All {len(english_to_x_pairs)} English→X pairs working!")

    @pytest.mark.parametrize("phrase_name,phrase_text", TEST_PHRASES.items())
    def test_english_phrases(self, english_to_x_pairs, phrase_name, phrase_text):
        """Test English phrases on English→X translations."""
        if not english_to_x_pairs:
            pytest.skip("No English→X pairs available")
            
        print(f"\n📝 Testing English '{phrase_name}': {phrase_text[:50]}...")
        
        failures = []
        for pair in english_to_x_pairs:
            from_name = pair['from_name']
            to_name = pair['to_name'] 
            translation = pair['translation']
            
            try:
                result = translation.translate(phrase_text)
                assert result and len(result.strip()) > 0, "Empty result"
                truncated_result = result[:50] + "..." if len(result) > 50 else result
                print(f"  ✓ {from_name}→{to_name}: '{truncated_result}'")
            except Exception as e:
                failures.append(f"{from_name}→{to_name}: {str(e)}")
                print(f"  ✗ {from_name}→{to_name}: {e}")
        
        if failures:
            pytest.fail(f"'{phrase_name}' failed on English→X pairs:\n" + "\n".join(failures))


class TestBidirectionalRoundTrip:
    """Test English→X→English round-trip translations."""
    
    def test_bidirectional_round_trip(self, english_to_x_pairs, all_translation_packages):
        """Test English→X→English round-trip translations."""
        if not english_to_x_pairs:
            pytest.skip("No English→X pairs available")
        
        # Create lookup for reverse translations
        reverse_lookup = {}
        for pkg in all_translation_packages:
            if pkg['to_code'] == 'en':
                reverse_lookup[pkg['from_code']] = pkg['translation']
        
        test_phrase = "Hello world"
        failures = []
        
        for i, pair in enumerate(english_to_x_pairs, 1):
            from_name = pair['from_name']
            to_name = pair['to_name']
            en_to_x = pair['translation']
            to_code = pair['to_code']
            
            print(f"\n[{i}/{len(english_to_x_pairs)}] EN→{to_name}→EN round-trip")
            
            try:
                # Step 1: English → X
                x_result = en_to_x.translate(test_phrase)
                assert x_result and len(x_result.strip()) > 0, "Empty forward translation"
                print(f"  EN→{to_name}: '{test_phrase}' → '{x_result}'")
                
                # Step 2: X → English (if reverse exists)
                x_to_en = reverse_lookup.get(to_code)
                if x_to_en:
                    en_result = x_to_en.translate(x_result)
                    assert en_result and len(en_result.strip()) > 0, "Empty reverse translation"
                    print(f"  {to_name}→EN: '{x_result}' → '{en_result}'")
                    print(f"  ✓ Round-trip complete: '{test_phrase}' → '{x_result}' → '{en_result}'")
                else:
                    print(f"  ⏭ No reverse translation available for {to_name}")
                
            except Exception as e:
                error_msg = f"EN→{to_name}→EN: {str(e)}"
                failures.append(error_msg)
                print(f"  ✗ FAILED: {e}")
        
        if failures:
            pytest.fail(f"{len(failures)} round-trip translations failed:\n" + "\n".join(failures))
        
        print(f"\n🎉 All round-trip translations completed!")
    
    @pytest.mark.parametrize("phrase_name,phrase_text", TEST_PHRASES.items())
    def test_round_trip_phrases(self, english_to_x_pairs, all_translation_packages, phrase_name, phrase_text):
        """Test round-trip translations for different phrases."""
        if not english_to_x_pairs:
            pytest.skip("No English→X pairs available")
        
        # Create lookup for reverse translations
        reverse_lookup = {}
        for pkg in all_translation_packages:
            if pkg['to_code'] == 'en':
                reverse_lookup[pkg['from_code']] = pkg['translation']
        
        print(f"\n📝 Testing round-trip for '{phrase_name}': {phrase_text[:50]}...")
        
        failures = []
        for pair in english_to_x_pairs:
            to_name = pair['to_name']
            to_code = pair['to_code']
            en_to_x = pair['translation']
            x_to_en = reverse_lookup.get(to_code)
            
            if not x_to_en:
                continue  # Skip if no reverse translation
            
            try:
                # EN → X → EN
                x_result = en_to_x.translate(phrase_text)
                assert x_result and len(x_result.strip()) > 0, "Empty forward translation"
                
                en_result = x_to_en.translate(x_result)
                assert en_result and len(en_result.strip()) > 0, "Empty reverse translation"
                
                truncated_x = x_result[:30] + "..." if len(x_result) > 30 else x_result
                truncated_en = en_result[:30] + "..." if len(en_result) > 30 else en_result
                print(f"  ✓ EN→{to_name}→EN: '{truncated_x}' → '{truncated_en}'")
                
            except Exception as e:
                failures.append(f"EN→{to_name}→EN: {str(e)}")
                print(f"  ✗ EN→{to_name}→EN: {e}")
        
        if failures:
            pytest.fail(f"'{phrase_name}' round-trip failed:\n" + "\n".join(failures))


class TestDirectionalOnly:
    """Test directional-only English pairs."""
    
    def test_directional_basic(self, directional_only_pairs):
        """Test basic translation for directional-only pairs."""
        if not directional_only_pairs:
            pytest.skip("No directional-only English pairs available")
            
        test_phrase = "Hello world"
        failures = []
        
        for i, pair in enumerate(directional_only_pairs, 1):
            from_name = pair['from_name']
            to_name = pair['to_name']
            translation = pair['translation']
            
            print(f"\n[{i}/{len(directional_only_pairs)}] {from_name} → {to_name} (one-way)")
            
            try:
                result = translation.translate(test_phrase)
                assert result and len(result.strip()) > 0, "Empty translation result"
                print(f"  ✓ '{test_phrase}' → '{result}'")
            except Exception as e:
                error_msg = f"{from_name} → {to_name}: {str(e)}"
                failures.append(error_msg)
                print(f"  ✗ FAILED: {e}")
        
        if failures:
            pytest.fail(f"{len(failures)} directional pairs failed:\n" + "\n".join(failures))
        
        print(f"\n🎉 All {len(directional_only_pairs)} directional-only pairs working!")


class TestNonEnglish:
    """Test non-English language pairs."""
    
    def test_non_english_basic(self, non_english_pairs):
        """Test basic translation for non-English pairs."""
        if not non_english_pairs:
            pytest.skip("No non-English pairs available")
            
        test_phrase = "Hello world"
        failures = []
        
        for i, pair in enumerate(non_english_pairs, 1):
            from_name = pair['from_name']
            to_name = pair['to_name']
            translation = pair['translation']
            
            print(f"\n[{i}/{len(non_english_pairs)}] {from_name} → {to_name}")
            
            try:
                result = translation.translate(test_phrase)
                assert result and len(result.strip()) > 0, "Empty translation result"
                print(f"  ✓ '{test_phrase}' → '{result}'")
            except Exception as e:
                error_msg = f"{from_name} → {to_name}: {str(e)}"
                failures.append(error_msg)
                print(f"  ✗ FAILED: {e}")
        
        if failures:
            pytest.fail(f"{len(failures)} non-English pairs failed:\n" + "\n".join(failures))
        
        print(f"\n🎉 All {len(non_english_pairs)} non-English pairs working!")


