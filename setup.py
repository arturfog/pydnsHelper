from setuptools import setup, find_packages
setup(
    name="dnsserver",
    version="0.1.0",
    packages=find_packages(),

    author="Artur Fogiel",
    license="GPLv3",
    url="https://github.com/arturfog/pydnsHelper",
    scripts=['manage.py']
)
