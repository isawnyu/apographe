import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="{distribution-name}",
    version="0.0.1",
    author="{author}",
    author_email="{author-email}",
    description="{short-description}",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    {project-url}
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: {pyver}",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['airtight'],
    python_requires='>={pyver}'
)
