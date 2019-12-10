from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=['multi_tracker_analysis','fly_plot_lib'],
    package_dir={'': '.'},
)
setup(**setup_args)
