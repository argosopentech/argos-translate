#! /usr/bin/env bash

# migrate files
# from Argos-Translate-LibreTranslate-2022-04-30.zip.torrent
# to   Argos-Translate-LibreTranslate-2022-04-30.torrent

# https://github.com/argosopentech/argos-translate/issues/375
# restructure the torrent: Argos-Translate-LibreTranslate-2022-04-30

# Argos-Translate-LibreTranslate-2022-04-30.zip.torrent
# is one zip file, which is bad practice for torrents
# users should be able to download only some model files

# this assumes that zip files are reproducible...
# see: packing new zip file

set -e

if [ $# != 1 ]; then
  echo "error: missing arguments"
  echo "usage:"
  echo "  $0 path/to/Argos-Translate-LibreTranslate-2022-04-30.zip"
  exit 1
fi

old_zip="$1"

if ! [ -e "$old_zip" ]; then
  echo "error: missing input file: $old_zip"
  exit 1
fi

if [ -e "Argos-Translate-LibreTranslate-2022-04-30" ]; then
  echo "error: output dir exists: Argos-Translate-LibreTranslate-2022-04-30"
  exit 1
fi

echo "migrating files from old torrent to new torrent. this will take about 7 minutes"

# simple integrity check
old_zip_size_expected=6747579574
old_zip_size=$(stat -L -c%s "$old_zip")
if [[ "$old_zip_size" != "$old_zip_size_expected" ]]; then
  echo "error: wrong size of input file. expected $old_zip_size_expected bytes"
  exit 1
fi

# proper integrity check
old_zip_hash_expected="b8ef6920d998454cca1ba4748c54ca2a2306e47942678f7ca81fa48a1f2bf488"
echo checking hash of input file. this will take about 2 minutes
time \
old_zip_hash=$(sha256sum "$old_zip" | cut -d' ' -f1)
if [[ "$old_zip_hash" != "$old_zip_hash_expected" ]]; then
  echo "error: wrong hash of input file"
  echo "  actual:   $old_zip_hash"
  echo "  expected: $old_zip_hash_expected"
  exit 1
fi

# sha256sum *.zip
new_zip_hash_expected_list="$(cat <<EOF
b15dfbb0299b352b4209c4f6226223c850659447391c60c932b7b177bdd9fd51  argos-translate-files.zip
47907f95dd3053a20bd0020c4d381ee93d27849c4db871914d76409b38f9986f  argos-translate-gui.zip
b4d306e43ff8927d99693e398c4bbbcbbf8fbf1535e1d6660aa888702a122913  argos-translate.zip
7dd00400a5fecb1bdd4d19a6e8c653cc3f06ebab5693a1acec1bf1ca53cfb0de  CTranslate2.zip
c81498054566c63578f42ec17781b365b601884077d4eeb30120110c035ef965  LibreTranslate-cpp.zip
ed564894f6edd3b2cd3fa94876058d37c3fc031fd75af31e7b271f7bb9e93174  libretranslate-go.zip
3628e46ad2f9fe7e5e594e59bb7899d170adcf9f875eb23db1703fce8775b4f5  LibreTranslate-init.zip
78972c3b27f4070519231c2576c2543dc334b35c64aa21bda8bae9aba608bb8b  libretranslate-php.zip
0788898ae45307a64190ae7921d30b6e8fb474f88b158ad9fea7330bc934f578  LibreTranslate-py.zip
bc82e9eb95aa3f07930125ed3f1a54c81ba041feea0f854f3999a7e5b3cabb47  libretranslate-rs.zip
0ac964c2acbcaae12580a58ead4eafdb80ad5c74e83092c1f1fa592ac926cbfd  LibreTranslate-sh.zip
23cbaaf8dffb2c6678080c9dad5b70c24a7640b653f92080cd0fbe70e734f82f  LibreTranslate.zip
889f90650f36b085b5e68447a7815f35000ca4da65602b090cb2479d232f481a  OpenNMT-py.zip
3585842220f7294dd61d6e859550069ed656c2f0c78b3c7debedc8fbbed0c171  OpenNMT-tf.zip
6556001eff3fee9847c712c1f9593785b598df9ebedb1e5cebd2baedfc98f835  sentencepiece.zip
cc80d801a238664b04d69d5fef57cf3e4ed7ce1dfbb5edf7af4edae2e2a8fe6b  stanza.zip
369452ed39193b57d0c32ff553a7b495f346d42d23e76ef9cba2a0f9537f96d7  Tokenizer.zip
a35f3b9e7f52677972ecfaa5be32ace99249da427cb24082dc0d2272ba3dc108  translate-html.zip
EOF
)"

echo unpacking the old zip file. this will take about 4 minutes
time \
unzip -q "$old_zip"

cd Argos-Translate-LibreTranslate-2022-04-30

echo packing new zip files. this will take about 1 minute
time {
  find . -mindepth 1 -maxdepth 1 -type d -printf "%P\n" |
  grep -v -x -e models -e dirs |
  while read dir; do
    if [ -e $dir.zip ]; then
      echo "error: new zip file exists: $dir.zip"
      continue
    fi
    echo packing new zip file: $dir.zip
    # already compressed files should be "stored" in the zip archives
    zip -q -r -n .zip:.xz:.gz:.bz2:.7z:.rar:.odp:.epub:.idx:.pack:.bin:.pt:.woff:.woff2:.png:.torrent $dir.zip $dir

    # check integrity
    new_zip_hash=$(sha256sum $dir.zip | cut -d' ' -f1)
    new_zip_hash_expected=$(echo "$new_zip_hash_expected_list" | grep "  $dir.zip$" | cut -d' ' -f1)
    if [[ "$new_zip_hash" != "$new_zip_hash_expected" ]]; then
      echo "error: wrong hash of output file: $dir.zip"
      echo "  actual:   $new_zip_hash"
      echo "  expected: $new_zip_hash_expected"
      echo "  keeping the folder $dir"
    else
      # remove the old files
      rm -rf $dir
    fi
  done
}

cd ..

cat <<EOF
done Argos-Translate-LibreTranslate-2022-04-30

next:

open the torrent Argos-Translate-LibreTranslate-2022-04-30.torrent

either from the torrent file
https://github.com/argosopentech/argos-translate/raw/master/p2p/Argos-Translate-LibreTranslate-2022-04-30.torrent

or from the magnet link
magnet:?xt=urn:btih:d1fb14d1b0f25e2e6f49d6dfd4ea761c445ad0d0&dn=Argos-Translate-LibreTranslate-2022-04-30

and set the download folder to
$(dirname "$(readlink -f Argos-Translate-LibreTranslate-2022-04-30)")

then your torrent client should use the existing files and start seeding
EOF
