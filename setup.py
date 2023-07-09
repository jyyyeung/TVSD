import os
from setuptools import find_packages, setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="tvsd",
    alias="tv_series_downloader",
    version="1.0.0-alpha.1",
    description="A sample Python package",
    author="JYYYEUNG",
    author_email="yeungjyy@gmail.com",
    url="https://github.com/SheepYY039/tv-series-download",
    project_urls={
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        # 'Source': 'https://github.com/pypa/sampleproject/',
        # 'Tracker': 'https://github.com/pypa/sampleproject/issues',
    },
    # packages=["tvsd"],
    packages=find_packages(include=["tvsd"]),
    # install_requires=[
    #     "numpy",
    #     "pandas",
    # ],
    long_description=read("README.md"),
    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # 开发的目标用户
        # "Intended Audience :: Developers",
        # 属于什么类型
        # "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        # 许可证信息
        "License :: OSI Approved :: MIT License",
        # 目标 Python 版本
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        # Environment
        "Environment :: Console",
    ],
    # entry_points={
    #     "console_scripts": [
    #         "tvsd = tvsd:quick_start",
    #     ]
    # },
)
