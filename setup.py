from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='femethods',
    version='0.1.7a1',
    author='Joseph Contreras',
    author_email='26684136+JosephJContreras@users.noreply.github.com',
    description='Implementation of Finite Element Analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://femethods.readthedocs.io/en/latest/index.html',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'scipy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
)
