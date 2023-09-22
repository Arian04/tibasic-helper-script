from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="tibasic-compile",
    version="1.0.0",
    url="https://gitea.arianb.me/arian/tibasic-script",
    author="Arian",
    install_requires=requirements,
    # license='GPL3',
    # scripts=["tibasic_compile.py"],
    entry_points={
        "console_scripts": [
            "tibasic-compile = tibasic_compile.tibasic_compile:main",
        ]
    },
)
