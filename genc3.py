#!/usr/bin/python3
# install ubuntu and debian:
#  sudo apt-get install libglfw3-dev

import os, sys, subprocess

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

## https://github.com/tonis2/opengl-c3.git
if not os.path.isdir('opengl-c3'):
	cmd = 'git clone --depth 1 https://github.com/tonis2/opengl-c3.git'
	print(cmd)
	subprocess.check_call(cmd.split())

def test_triangle():
	cmd = [C3, 'run', 'triangle']
	print(cmd)
	subprocess.check_call(cmd, cwd='c3-opengl-examples')


def test_c3(output='test-c3-glfw.bin'):
	cmd = [
		C3, 
		'--target', 'linux-x64',
		'--output-dir', '/tmp',
		'--obj-out', '/tmp',
		'--build-dir', '/tmp',
		'--print-output',
		'-o', output,

		'-l', 'glfw',

		'compile', 

		'./c3-opengl-examples/examples/tri.c3',
		'./opengl-c3/build/gl.c3',
		'./c3-opengl-examples/dependencies/glfw.c3',
		'./c3-opengl-examples/dependencies/helpers.c3',

	]
	print(cmd)
	subprocess.check_call(cmd)
	subprocess.check_call(['/tmp/'+output])

if __name__=='__main__':
	if '--simple' in sys.argv:
		test_triangle()
	else:
		test_c3()
