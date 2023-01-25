import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="emvoip",
    version="1.0.3",
    author="Emmanuel Okwudike",
    author_email="okwudike.emmanuel@gmail.com",
    description="a more comprehensive python wrapper for twilio services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='emvoip pywrapper voice twilio api',
    url="https://github.com/iameo/em-voip",
    project_urls={
        "Bug Tracker": "https://github.com/iameo/em-voip/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    python_requires=">=3.6",
)