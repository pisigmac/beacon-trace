from setuptools import setup, find_packages

setup(
    name="beacon-trace",
    version="1.0.0",
    description="Local-first observability SDK for AI agents",
    packages=find_packages(),
    install_requires=["requests>=2.28.0"],
    python_requires=">=3.8",
    author="Beacon Team - Vikas Budde",
    url="https://github.com/pisgimac/beacon-trace",
)
