import setuptools

setuptools.setup(
    name='mkdocs-ultirepo-plugin',
    version='0.1.1',
    description='Plugin for adding the ultimate multiple repo support in Mkdocs.',
    long_description="""This plugin is built to be easily extended with different parsers called 'include'.
    These 'include' parsers can have advanced behavior like pulling a git repo and extracting the relevant documentation from it to merge with the parent.
    The resolver is designed to recursively resolve the documentation and navigation indefinitely, however the default value for max nested includes are set to 1""",  # noqa: E501
    keywords='mkdocs ultirepo',
    url='https://github.com/emil-jacero/mkdocs-ultirepo-plugin',
    author='Emil Larsson',
    author_email='emil@jacero.se',
    license='MIT Licence',
    python_requires='>=3.10',
    install_requires=[
        'mkdocs>=1.4.0',
        'python-slugify>=4.0.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'mkdocs.plugins': [
            "ultirepo = mkdocs_ultirepo_plugin.plugin:UltirepoPlugin"
        ]
    }
)