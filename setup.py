from setuptools import setup, find_packages

setup(
    name="win-services-observer",
    version="1.0.0",
    description="Observability tool for Windows services",
    author="Gelu Liuta",
    author_email="gelu.liuta@gmail.com",
    packages=find_packages("src"),
    package_dir={"":"src"}
    #install_requires=['prometheus_client']
)