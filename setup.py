import os
import setuptools

# try to grab the parent folder
ex_dir = os.path.dirname(os.path.abspath(__file__))
# try to convert README.md to reStructuredTest (.rst) for PyPI
readme_path = os.path.join(ex_dir, 'README.md')

# open the read me file
if os.path.isfile(readme_path):
    with open(readme_path, "r") as fd:
        long_description = fd.read()
else:
    long_description = ""

setuptools.setup(
    name='gpurelperf',
    version='1.0.5',
    url='https://github.com/andylamp/gpurelperf',
    license='Apache 2.0',
    author='Andreas Grammenos',
    author_email='andreas.grammenos@gmail.com',
    description='A python utility to find relative GPU performance in multi-gpu boxes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # require at least Python 3.4
    python_requires='>=3.4',
    install_requires=['requests'],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
    zip_safe=False
)
