from setuptools import setup, find_packages

setup(name='boring_battery',
      version='1.0.0',
      packages=find_packages(),
      #py_modules=['example1'],
      install_requires=[
        'openmdao',
        'dymos @ git+https://git@github.com/OpenMDAO/dymos',
        'pyoptsparse @ git+https://github.com/mdolab/pyoptsparse@v1.2',
        'matplotlib',
        'scipy',
        'pandas',
        'lcapy',
        'testflo',
      ]
)
