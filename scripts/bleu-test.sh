cat input.ru | while read LINE; do
    ./bin/argos-translate --from-lang=ru --to-lang=en "$LINE" >> output.en
done
