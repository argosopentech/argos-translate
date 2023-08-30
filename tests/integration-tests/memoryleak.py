import argostranslate.package
import argostranslate.translate

from_code = "en"
to_code = "es"

# Translate
while True:
    translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
    print(translatedText)