from setuptools import setup, find_packages

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Add development dependencies
dev_dependencies = [
    "pytest",
    "pytest-cov",
    "flake8",
    "black",
    "mypy",
    "tox",
    "pre-commit",
]

setup(
    name="weatherlink",
    version="1.0.0",
    packages=find_packages(where="src") + ["tests"],
    package_dir={"": "src", "tests": "tests"},
    install_requires=requirements,
    extras_require={
        "dev": dev_dependencies,
    },
    # Add other metadata and configuration options as needed
)
