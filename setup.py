import os
import Cython

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

directive_defaults = Cython.Compiler.Options.get_directive_defaults()

LANG = 'c++'
os.environ["CC"] = LANG
os.environ["CXX"] = LANG

directive_defaults['linetrace'] = True
directive_defaults['binding'] = True


# pass the following to enable line profiling
# define_macros=[('CYTHON_TRACE', '1')]

extensions = [
    Extension(
        'core1', ['core1.pyx'],
        language=LANG,
        libraries=["m"]
    ),
    Extension(
        'si', ['si.pyx'],
        language=LANG
    )
]

setup(
    name="name",
    ext_modules=cythonize(extensions),
)
