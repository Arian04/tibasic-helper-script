from setuptools import setup

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="tibasic-compile",
    version="1.0.0",
    url="https://gitea.arianb.me/arian/tibasic-script",
    # author='Arian',
    # author_email='lowe.thiderman@gmail.com',
    # description=('wow very terminal doge'),
    # license='MIT',
    # packages=['doge'],
    # package_data={'doge': ['static/*.txt']},
    scripts=["tibasic-compile.py"],
)
