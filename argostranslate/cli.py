import argparse
import sys
from argostranslate import package, translate

def main():
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='?', help='The text to translate')
    parser.add_argument('--from-lang',
            help='The code for the language to translate from (ISO 639-1)')
    parser.add_argument('--to-lang',
            help='The code for the language to translate to (ISO 639-1)')
    args = parser.parse_args()

    # Get text to translate
    if args.text:
        # argos-translate-cli --from-lang en --to-lang es "Text to translate"
        text_to_translate = args.text
    else :
        # echo "Text to translate" | argos-translate-cli --from-lang en --to-lang es
        text_to_translate = ''
        for line in sys.stdin:
            text_to_translate += line

    # Perform translation
    if args.from_lang != None and args.to_lang != None:
        installed_languages = translate.load_installed_languages()
        from_lang_index = None
        for i, lang in enumerate(installed_languages):
            if lang.code == args.from_lang:
                from_lang_index = i
                break
        to_lang_index = None
        for i, lang in enumerate(installed_languages):
            if lang.code == args.to_lang:
                to_lang_index = i
                break
        from_lang = installed_languages[from_lang_index]
        to_lang = installed_languages[to_lang_index]
        translation = from_lang.get_translation(to_lang)
        if translation == None:
            sys.exit('No translation installed from {} to {}'.format(
                    args.from_name, args.to_name))
    else:
        translation = translate.IdentityTranslation('')

    # Print translation
    print(translation.translate(text_to_translate))

