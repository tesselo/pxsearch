import os

from setuptools import find_packages, setup

with open("requirements.in") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]

setup(
    name="pxsearch",
    version=os.getenv("PACKAGE_VERSION") or "0.0.1",
    url="https://github.com/tesselo/pxsearch",
    author="Keren Vasconcelos",
    author_email="keren@tesselo.com",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "Private :: Do Not Upload",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    entry_points={"console_scripts": ["pxsearch=pxsearch.app:main"]},
)
