from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name='Argos Translate',
    version='1.0',
    description='Offline translation app',
    author='Argos Open Technologies, LLC',
    author_email='admin@argosopentech.com',
    url='https://www.argosopentech.com',
    packages=find_packages(),
    install_requires=required_packages,
    include_package_data=True,
    scripts=['bin/argos-translate'],
)
