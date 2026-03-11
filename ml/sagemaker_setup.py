"""
ml/sagemaker_setup.py
Dependency setup script bundled into sourcedir.tar.gz alongside inference.py.

SageMaker runs this automatically inside the container before loading the model.
It upgrades numpy, scikit-learn, and pandas to versions compatible with the pkl
files (which were saved with numpy 2.x).

Without this, the container's default numpy 1.x cannot load the pkl files and
throws: ModuleNotFoundError: No module named 'numpy._core.multiarray'
"""

from setuptools import setup

setup(
    name="inference",
    version="1.0.0",
    install_requires=[
        "numpy>=2.0",
        "scikit-learn>=1.4",
        "pandas>=2.0",
    ],
    py_modules=["inference"],
)
