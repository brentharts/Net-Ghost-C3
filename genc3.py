#!/usr/bin/python3
# install ubuntu and debian: sudo apt-get install libglfw3-dev
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

def test_c3(output='test-c3-glfw.bin', opt='--opt' in sys.argv, wasm='--wasm' in sys.argv):
	if opt:
		output = output.replace('.bin', '.opt.bin')
	if wasm:
		output = output.replace('.bin', '.wasm.bin')

	cmd = [C3]
	if wasm:
		cmd += [
			'--target', 'wasm32',
			'--linker=custom', './emsdk/upstream/bin/wasm-ld'
		]
	else:
		cmd += ['--target', 'linux-x64']
	mode = 'compile'

	cmd += [
		'--output-dir', '/tmp',
		'--obj-out', '/tmp',
		'--build-dir', '/tmp',
		'--print-output',
		'-o', output,
	]
	if wasm:
		cmd += [#'--link-libc=no', '--use-stdlib=no', 
			'--no-entry', '--reloc=none']
		pass
	else:
		cmd += ['-l', 'glfw']

	if opt:
		cmd.append('-Oz')

	cmd += [
		mode, 
		'./c3-opengl-examples/examples/tri.c3',
		'./opengl-c3/build/gl.c3',
		'./c3-opengl-examples/dependencies/glfw.c3',
		'./c3-opengl-examples/dependencies/helpers.c3',

	]
	print(cmd)
	res = subprocess.check_output(cmd).decode('utf-8')
	ofiles = []
	for ln in res.splitlines():
		if ln.endswith('.o'):
			ofiles.append(ln.strip())
	print(ofiles)
	os.system('ls -lh /tmp/*.bin')
	os.system('ls -lh /tmp/*.o')

	if '--run' in sys.argv:
		subprocess.check_call(['/tmp/'+output])
	if wasm:
		cmd = ['./emsdk/upstream/bin/llvm-objdump', '--syms', '/tmp/'+output+'.wasm']
		print(cmd)
		subprocess.check_call(cmd)

if __name__=='__main__':
	if '--simple' in sys.argv:
		test_triangle()
	else:
		test_c3()
