from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sequence_pickler',
    version='1.0.2',
    description='A library to save a sequence and load it later.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/masamitsu-murase/sequence_pickler',
    author='Masamitsu MURASE',
    author_email='masamitsu.murase@gmail.com',
    license='MIT',
    keywords='pickle',
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=True,
    python_requires='>=3.8.*, <4',
    install_requires=[],
    extras_require={'test': [], 'package': ['wheel', 'twine']},
    project_urls={
        'Bug Reports':
        'https://github.com/masamitsu-murase/sequence_pickler/issues',
        'Source': 'https://github.com/masamitsu-murase/sequence_pickler',
    },
)
