from setuptools import setup, find_packages
import toml
from pathlib import Path

pyproject_path = str(Path(__file__).parent / 'pyproject.toml')
file = open(pyproject_path, "r")
toml_str = file.read()

parsed_toml = toml.loads(toml_str)

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pyFoamd',
    version=parsed_toml['tool']['commitizen']['version'],
    description='Pythonic interface for OpenFOAM dictionaries and case files.',
    entry_points = {
        'console_scripts': [
            'pf = pyfoamd.__main__:main'
        ]
    },
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Marc Goldbach',
    author_email='mcgoldba@gmail.com',
    url='https://github.com/mcgoldba/pyFoamd',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.7',
    install_requires=[
        'pint',
        'pandas',
        'rich',
        'ipython'
    ]
)
