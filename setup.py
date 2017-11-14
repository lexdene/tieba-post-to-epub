from setuptools import setup, find_packages


def get_long_description():
    with open('README.rst') as f:
        return f.read()


name = 'tieba-to-epub'
main_module_name = name.replace('-', '_')

setup(
    name=name,
    version='0.0.2',
    description='convert baidu tieba post to epub',
    long_description=get_long_description(),
    author='Elephant Liu',
    author_email='elephant_liu@mail.dlut.edu.cn',
    url='https://github.com/lexdene/tieba-post-to-epub',
    license='GPLv3',
    packages=find_packages(exclude=['tests']),
    package_data={main_module_name: ['templates/*']},
    install_requires=[
        'aiohttp',
        'lxml',
        'ebooklib',
        'Jinja2>=2.9',  # Jinja2 supports async since 2.9
    ],
    entry_points={
        'console_scripts': [
            '%s = %s.main:main' % (name, main_module_name)
        ]
    },
    platforms=['any'],
)
