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
    name="skyentific",
    version="1.0.0",
    packages=find_packages(where="src") + ["tests", "scripts"],
    package_dir={"": "src", "tests": "tests", "scripts": "scripts"},
    install_requires=requirements,
    extras_require={
        "dev": dev_dependencies,
    },
    entry_points={
        "console_scripts": [
            "skyentific=scripts.skyentific:main",
        ],
    },
    # Add other metadata and configuration options as needed
)
