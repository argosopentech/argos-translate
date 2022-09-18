import argparse
import os
from pathlib import Path

import sacrebleu

from argostranslate.translate import translate


def main():
    parser = argparse.ArgumentParser(description="sacreBLEU score for a model")
    parser.add_argument(
        "--test-set",
        "--t",
        default="wmt17",
        metavar="TEST_SET",
        help="The test set",
    )
    parser.add_argument(
        "--lang-pair",
        "--l",
        metavar="LANG_PAIR",
        help="The lang pair of the model to test",
    )
    args = parser.parse_args()

    test_set = args.test_set
    lang_pair = args.lang_pair

    splitted_lang_pair = lang_pair.split('-')
    from_lang = splitted_lang_pair[0]
    to_lang = splitted_lang_pair[1]

    sacrebleu.download_test_set(test_set, lang_pair)
    source_file_path = Path(sacrebleu.get_source_file(test_set, lang_pair))

    output_file_path = test_set + '.output.' + lang_pair
    output_file = open(output_file_path, "a+", encoding="utf-8")

    with open(source_file_path, "r") as source:
        lines = source.readlines()
        source_lines = [line.strip() for line in lines]
        source_lines_length = len(source_lines)

        for i, line in enumerate(source_lines):
            translated = translate(line, from_lang, to_lang)
            print('Translated ' + str(i) + ' lines of ' + str(source_lines_length) + ' lines')

            output_file.write(translated.strip() + "\n")
            output_file.flush()

    os.system(
        "sacrebleu -i " + output_file_path + " -t " + test_set + " -l " + lang_pair + ' >> ' + lang_pair + '.sacrebleu-score.json')


main()
