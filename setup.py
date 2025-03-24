from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rapid-bookingcom",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python SDK for interacting with Booking.com APIs through RapidAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rapid-bookingcom",
    packages=find_packages(),
    package_data={
        'rapid_bookingcom': ['examples/*.py'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rapid-bookingcom=py_flights_sdk.__main__:main",
        ],
    },
)