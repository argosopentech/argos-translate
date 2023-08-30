import argostranslate.package
import argostranslate.translate

from_code = "en"
to_code = "es"

# Translate
for i in range(100000):
    translatedText = argostranslate.translate.translate(
        "Hello World", from_code, to_code
    )
    if i % 100 == 0:
        print(i)
