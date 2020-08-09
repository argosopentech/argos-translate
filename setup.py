from setuptools import setup, find_packages

setup(
    name='Argos Translate',
    version='1.0',
    description='Offline translation app',
    author='Argos Open Technologies, LLC',
    author_email='admin@argosopentech.com',
    url='https://www.argosopentech.com',
    packages=find_packages(),
    scripts=['bin/argos-translate']
)
