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
        installed_languages = {
            lang.code: lang
            for lang in translate.load_installed_languages()}
        if args.from_lang not in installed_languages:
            parser.error('{!r} is not an installed language.'.format(
                args.from_lang))
        if args.to_lang not in installed_languages:
            parser.error('{!r} is not an installed language.'.format(
                args.to_lang))
        from_lang = installed_languages[args.from_lang]
        to_lang = installed_languages[args.to_lang]
        translation = from_lang.get_translation(to_lang)
        if translation is None:
            parser.error('No translation installed from {!r} to {!r}'.format(
                args.from_name, args.to_name))
    else:
        translation = translate.IdentityTranslation('')

    # Print translation
    print(translation.translate(text_to_translate))
