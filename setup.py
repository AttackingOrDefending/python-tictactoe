import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-tictactoe",
    version="0.0.1",
    author="AttackingOrDefending",
    description="A tictactoe library for Python with varying board sizes and move generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AttackingOrDefending/python-tictactoe",
    project_urls={
        "Bug Tracker": "https://github.com/AttackingOrDefending/python-tictactoe/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["tictactoe"],
    python_requires=">=3.6",
    install_requires=["numpy==1.22.1"],
)
