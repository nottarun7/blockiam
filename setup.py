"""Setup script for BlockIAM package"""

from setuptools import setup, find_packages

setup(
    name="blockiam",
    version="0.1.0",
    description="Python library for blockchain-based IoT device identity and access management",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "web3>=6.0.0",
        "python-dotenv>=0.19.0",
        "rich>=12.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "blockiam=iot_iam.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "iot_iam": ["../ABI.json"],
    },
)
