from setuptools import setup, find_packages

version = '0.1'

setup(name='plonezoho.remoteeditor',
      version=version,
      description="Zoho Editor  integratied into Plone",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='plone zoho editor remote',
      author='Rok Garbas',
      author_email='rok@garbas.si',
      url='http://github.com/collective/plonezoho.remoteeditor',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plonezoho'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zohoapi',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
