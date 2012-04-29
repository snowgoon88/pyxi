from distutils.core import setup

setup( name='pyxitag',
       version='0.01',
       py_modules=['tag_data'],
       author='Alain Dutech',
       author_email='snowgoon88@gmail.com',
       url='http://nothing.yet.org',
       description='Tagging photo using EXIF-like metadata',
       requires=['gtk','xml.etree.ElementTree']
       )
