from setuptools import setup

setup(
    name="smart_settings",
    version="1.1",
    description="Smart JSON setting files",
    url="https://github.com/mrolinek",
    author="Michal Rolinek, MPI-IS Tuebingen, Autonomous Learning",
    author_email="michalrolinek@gmail.com",
    license="MIT",
    packages=["smart_settings"],
    install_requires=[
        "pyyaml",
        "tomli; python_version < '3.11'",
    ],
    zip_safe=False,
)
