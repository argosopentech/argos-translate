import argostranslate.package
import argostranslate.translate
import urllib.request

# 모델 다운로드 URL (최신 주소는 GitHub releases에서 확인 필요)
package_url = "https://github.com/argosopentech/argospm-packages/releases/download/en_ko-1_0_0/en_ko.argosmodel"

# 모델 파일 임시로 다운로드
package_path, _ = urllib.request.urlretrieve(package_url)

# 다운로드한 모델 설치
argostranslate.package.install_from_path(package_path)

# 설치된 언어 로드
argostranslate.translate.load_installed_languages()

print("번역 모델 설치 완료")