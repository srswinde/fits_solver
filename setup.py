#!/usr/bin/env python

#this is the setup file

from distutils.core import setup
import os

setup(name='fits_solver',
      version='1.0',
      description='Python Distribution Utilities',
      author='Scott Swindell',
      author_email='scottswindell@email.arizona.edu',
	  packages = ['fits_solver'],
	  package_dir = {'':'src'},
	  scripts = [
		'src/fits_solver/slotis_imclient.py',
		'src/fits_solver/imserver.py',
		
		],
     )
