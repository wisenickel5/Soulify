from setuptools import setup, find_packages

setup(
    name = "Soulify",
    version = "1.0",
    url = "https://soulify.herokuapp.com/",
    description = "",
    author = "Dylan Alexander",
    author_email = "dalexa75@students.kennesaw.edu",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'Flask',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Spotify Users',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)