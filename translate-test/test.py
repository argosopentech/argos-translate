import argostranslate.package
import argostranslate.translate

package_path = r"C:\Users\hureu\Downloads\translate-en_ko-1_1.argosmodel"

# 모델 설치
argostranslate.package.install_from_path(package_path)

installed_languages = argostranslate.translate.get_installed_languages()
print("설치된 언어 목록:", installed_languages)

if len(installed_languages) == 0:
    print("⚠️ 설치된 번역 모델이 없습니다.")
else:
    translated_text = argostranslate.translate.translate("The objective of our research is to create an agent-based environment within which meeting scheduling can be performed and optimized", "en", "ko")
    print("번역 결과:", translated_text)