from setuptools import setup, find_packages

setup(
    name="HubCoreService",
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    author="krushit-navicogroup",
    author_email="krushit.patel@navicogroup.com",
    description="Hub Core - Python",
    license="MIT",
    keywords=["interface", "led", "ble", "lte", "wifi", "hub", "navico"],
    install_requires=["pyserial", "psutil", "typeguard"],
    url="https://github.com/NavicoGroup/empower-hub-host/tree/main/HubCoreService",
)
