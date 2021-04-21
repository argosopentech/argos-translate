import argparse
import sys
from argostranslate import package, translate


def main():
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='?', help='The text to translate')
    parser.add_argument(
        '-f', '--from-lang', help='The code for the language to translate from (ISO 639-1)'
    )
    parser.add_argument(
        '-t', '--to-lang', help='The code for the language to translate to (ISO 639-1)'
    )
    args = parser.parse_args()

    from_and_to_lang_provided = args.from_lang is not None and args.to_lang is not None

    # Get text to translate
    if args.text:
        # argos-translate-cli --from-lang en --to-lang es "Text to translate"
        text_to_translate = args.text
    elif from_and_to_lang_provided:
        # echo "Text to translate" | argos-translate-cli --from-lang en --to-lang es
        text_to_translate = ''
        for line in sys.stdin:
            text_to_translate += line
    else:
        # argos-translate
        parser.print_help()
        return

    # Perform translation
    if from_and_to_lang_provided:
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
            raise Exception(f'No translation installed from {args.from_name} to {args.to_name}')
    else:
        translation = translate.IdentityTranslation('')

    # Print translation
    print(translation.translate(text_to_translate))
