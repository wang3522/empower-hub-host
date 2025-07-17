from setuptools import setup, find_packages

setup(
    name="n2kclient",
    version="0.1.0",
    description="A Python library for interfacing with N2K devices.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        #MAC NEEDS brew install pkg-config dbus pygobject3 gtk+3 first
        "PyGObject==3.52.3",
        "dbus-python==1.4.0",
        "reactivex==4.0.4"
    ],
    python_requires=">=3.7",
    url="https://github.com/yourusername/n2kclient",  # Update as needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)