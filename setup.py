from setuptools import setup

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="tibasic-compile",
    version="1.0.0",
    url="https://gitea.arianb.me/arian/tibasic-script",
    # author='Arian',
    # license='GPL3',
    scripts=["tibasic-compile.py"],
)
