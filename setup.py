import setuptools, insight_cli


setuptools.setup(
    name="insight-cli",
    version=insight_cli.__version__,
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ["insight = insight_cli:insight_cli"],
    },
    install_requires=[
        "requests==2.31.0",
    ],
)
