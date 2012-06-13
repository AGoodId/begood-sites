from distutils.core import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="begood-sites",
    version="0.1.0",
    description="",
    author="AGoodId",
    author_email="teknik@agoodid.com",
    maintainer="AGoodId",
    maintainer_email="teknik@agoodid.se",
    url="https://github.com/agoodid/begood-sites",
    license="MIT",
    packages=[
        "begood_sites",
        "begood_sites.management.commands",
    ],
    long_description=read("README.markdown"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
)
