#!/usr/bin/python3
import os, sys, subprocess, ctypes, time, json, webbrowser
from random import random, uniform

_thisdir = os.path.split(os.path.abspath(__file__))[0]

if not os.path.isdir('zig-bootstrap'):
	cmd = 'git clone --depth 1 https://github.com/ziglang/zig-bootstrap.git'
	print(cmd)
	subprocess.check_call(cmd.split())

if not os.path.isdir('mach'):
	cmd = 'git clone --depth 1 https://github.com/hexops/mach.git'
	print(cmd)
	subprocess.check_call(cmd.split())


if not os.path.isdir('./zig-bootstrap/out') or '--rebuild-zig' in sys.argv:
	if '--native' in sys.argv:
		cmd = './build x86_64-linux-gnu native'
	else:
		cmd = './build x86_64-linux-gnu baseline'
	print(cmd)
	subprocess.check_call(cmd.split(), cwd='./zig-bootstrap')
