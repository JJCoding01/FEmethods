from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='femethods',
    version='0.1.5dev',
    author='Joseph Contreras',
    author_email='26684136+JosephJContreras@users.noreply.github.com',
    description='Implementation of Finite Element Analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/josephjcontreras/FEMethods.git',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'scipy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
)
