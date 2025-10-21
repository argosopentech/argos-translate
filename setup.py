from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="argostranslate",
    version="1.10.0",
    description="Open-source neural machine translation library based on OpenNMT's CTranslate2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Argos Open Technologies, LLC",
    author_email="admin@argosopentech.com",
    url="https://www.argosopentech.com",
    project_urls={
        "Website": "https://www.argosopentech.com",
        "Documentation": "https://argos-translate.readthedocs.io/en/latest/",
        "GitHub": "https://github.com/argosopentech/argos-translate",
        "Forum": "https://community.libretranslate.com/c/argos-translate/5",
    },
    python_requires=">=3.5",
    packages=find_packages(),
    install_requires=required_packages,
    entry_points={
        "console_scripts": [
            "argos-translate = argostranslate.cli:main",
            "argospm = argostranslate.argospm:main",
        ]
    },
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
    ],
)
