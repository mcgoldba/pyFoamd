from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pyFoamd',
    version='0.1.0',
    description='Pythonic interface for OpenFOAM dictionaries and case files.',
    entry_points = {
        'console_scripts': [
            'pf = pyfoamd.__main__:main'
        ]
    },
    long_description=readme,
    author='Marc Goldbach',
    author_email='mcgoldba@gmail.com',
    url='https://github.com/mcgoldba/pyFoamd',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.7',
    install_requires=[
        'pint',
        'pandas',
        'rich'
    ]
)
