from setuptools import setup, find_packages

setup(
    name='tieba-to-epub',
    version='0.0.1',
    description='convert baidu tieba post to epub',
    long_description='',
    author='Elephant Liu',
    author_email='elephant_liu@mail.dlut.edu.cn',
    url='https://github.com/lexdene/tieba-post-to-epub',
    license='GPLv3',
    packages=find_packages(exclude=['tests']),
    package_data={'tieba_to_epub': ['templates/*']},
    install_requires=[
        'aiohttp',
        'lxml',
        'ebooklib',
        'Jinja2>=2.9',  # Jinja2 supports async since 2.9
    ],
    entry_points={
        'console_scripts': [
            'tieba-to-epub = tieba_to_epub.main:main'
        ]
    },
    platforms=['any'],
)
