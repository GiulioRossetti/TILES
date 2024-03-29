from setuptools import setup, find_packages

__author__ = 'Giulio Rossetti'
__license__ = "BSD 2 Clause"
__email__ = "giulio.rossetti@gmail.com"

# Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()

setup(name='tiles',
      version='1.0.4',
      license='BSD-2-Clause',
      description='Dynamic Community Discovery algorithm',
      url='https://github.com/GiulioRossetti/TILES',
      author='Giulio Rossetti',
      author_email='giulio.rossetti@gmail.com',
      # Removed, causing error on setup
      #use_2to3=True,
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: BSD License',

          "Operating System :: OS Independent",

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3'
      ],
      keywords=['complex-networks', 'dynamic community discovery', 'dynamic networks'],
      install_requires=['networkx',  'future', ''],
      packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test", "tiles.test", "tiles.test.*"]),
      )
