from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="argostranslate",
    version="1.7.0",
    description="Offline neural machine translation library and GUI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Argos Open Technologies, LLC",
    author_email="admin@argosopentech.com",
    url="https://www.argosopentech.com",
    project_urls={
        "Documentation": "https://argos-translate.readthedocs.io/en/latest/",
        "Source": "https://github.com/argosopentech/argos-translate",
    },
    packages=find_packages(),
    install_requires=required_packages,
    include_package_data=True,
    scripts=["bin/argos-translate", "bin/argospm"],
)
