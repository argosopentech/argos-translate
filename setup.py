from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="argostranslate",
    version="1.6.0",
    description="Offline neural machine translation library and GUI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Argos Open Technologies, LLC",
    author_email="admin@argosopentech.com",
    url="https://www.argosopentech.com",
    packages=find_packages(),
    install_requires=required_packages,
    include_package_data=True,
    scripts=["bin/argos-translate", "bin/argos-translate-gui", "bin/argospm"],
)
