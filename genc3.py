#!/usr/bin/python3
# install ubuntu and debian:
#  sudo apt-get install libglfw3-dev


#import os, sys, subprocess, ctypes, time, json, webbrowser
#from random import random, uniform
#_thisdir = os.path.split(os.path.abspath(__file__))[0]
import os, subprocess

if not os.path.isfile('c3-ubuntu-20.tar.gz'):
	cmd = 'wget -c https://github.com/c3lang/c3c/releases/download/latest/c3-ubuntu-20.tar.gz'
	print(cmd)
	subprocess.check_call(cmd.split())


if not os.path.isdir('c3'):
	cmd = 'tar -xvf c3-ubuntu-20.tar.gz'
	print(cmd)
	subprocess.check_call(cmd.split())

C3 = os.path.abspath('./c3/c3c')
assert os.path.isfile(C3)

#if not os.path.isdir('opengl-examples'):
#	cmd = 'git clone --depth 1 https://github.com/tonis2/opengl-examples.git'
#	print(cmd)
#	subprocess.check_call(cmd.split())
if not os.path.isdir('c3-opengl-examples'):
	cmd = 'git clone --depth 1 https://github.com/brentharts/c3-opengl-examples.git'
	print(cmd)
	subprocess.check_call(cmd.split())


cmd = [C3, 'run', 'triangle']
print(cmd)
subprocess.check_call(cmd, cwd='c3-opengl-examples')

