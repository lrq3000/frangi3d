from setuptools import setup

version = "0.1.0"

with open("./README.md") as fd:
    long_description = fd.read()


setup(
    name="frangi3d",
    description="3D Frangi / Vesselness filter",
    long_description=long_description,
    install_requires=[
        "numpy",
        "scipy"
    ],
    packages=["frangi"],
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'
    ]
)