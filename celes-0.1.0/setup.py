from setuptools import setup, find_packages

setup(
    name="celes",
    version="0.1.4",
    description="Celes 0.1 — a tag-based markup language toolkit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="SOCL-1.0",
    python_requires=">=3.8",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "celes=celes.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup",
    ],
)
