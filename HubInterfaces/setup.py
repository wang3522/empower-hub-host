from setuptools import setup, find_packages

setup(
    name="HubInterfaces",
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    author="krushit-navicogroup",
    author_email="krushit.patel@navicogroup.com",
    description="Hub Interfaces - Python",
    license="MIT",
    keywords=["interface", "led", "ble", "lte", "wifi", "hub", "navico"],
    install_requires=["pyserial", "psutil", "typeguard"],
    url="https://github.com/NavicoGroup/empower-hub-host/tree/krushit-dev/HubInterfaces",
)
