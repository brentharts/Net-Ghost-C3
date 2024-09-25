#!/usr/bin/python3
import os, sys, subprocess, ctypes, time, json, webbrowser
from random import random, uniform

_thisdir = os.path.split(os.path.abspath(__file__))[0]
EMSDK = os.path.join(_thisdir, "emsdk")
BLENDER = 'blender'

def emsdk_update():
	subprocess.check_call(["git", "pull"], cwd=EMSDK)
	subprocess.check_call(["./emsdk", "install", "latest"], cwd=EMSDK)
	subprocess.check_call(["./emsdk", "activate", "latest"], cwd=EMSDK)


if "--wasm" in sys.argv and not os.path.isdir(EMSDK):
	cmd = [
		"git",
		"clone",
		"--depth",
		"1",
		"https://github.com/emscripten-core/emsdk.git",
	]
	print(cmd)
	subprocess.check_call(cmd)
	emsdk_update()

EMCC = os.path.join(EMSDK, "upstream/emscripten/emcc")
if not EMCC and "--wasm" in sys.argv:
	emsdk_update()

def test_glfw(output='/tmp/test-glfw.html'):
	tmp = '/tmp/test-glfw.c++'
	o = [TEST_DATA, TEST_GLFW]
	open(tmp, 'w').write('\n'.join(o))
	cmd = [
		EMCC, '-o', output, 
		'-std=c++1z', 
		"-s","FETCH",
		"-s","SINGLE_FILE",
		"-s","ENVIRONMENT=web",
		"-s","WASM=1",
		"-s","AUTO_JS_LIBRARIES",
		"-s","USE_WEBGL2=1",
		"-s","USE_GLFW=3",
		"-s","NO_FILESYSTEM=1",
		'-I', _thisdir, 
		tmp
	]
	print(cmd)
	subprocess.check_call(cmd)

TEST_DATA = '''
struct Verts2D{
	float x, y;
	float r, g, b;
};

static const Verts2D vertices[3] = {
	{-0.6f, -0.4f, 1.f, 0.f, 0.f},
	{0.6f, -0.4f, 0.f, 1.f, 0.f},
	{0.f, 0.6f, 0.f, 0.f, 1.f}
};
'''

## https://gist.github.com/ousttrue/0f3a11d5d28e365b129fe08f18f4e141
## https://github.com/glfw/glfw/blob/master/deps/linmath.h
TEST_GLFW = r'''
// emcc main.cpp -o index.html -s USE_WEBGL2=1 -s USE_GLFW=3 -s WASM=1 -std=c++1z

// base:  https://www.glfw.org/docs/latest/quick.html#quick_example
// ref: https://gist.github.com/SuperV1234/5c5ad838fe5fe1bf54f9

#include <functional>
#include <vector>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#define GL_GLEXT_PROTOTYPES
#define EGL_EGLEXT_PROTOTYPES
#else
#include <glad/glad.h>
#endif
#include <GLFW/glfw3.h>
#include "linmath.h"
#include <stdlib.h>
#include <stdio.h>



static const char *vertex_shader_text =
	"uniform mat4 MVP;\n"
	"attribute vec3 vCol;\n"
	"attribute vec2 vPos;\n"
	"varying vec3 color;\n"
	"void main()\n"
	"{\n"
	"    gl_Position = MVP * vec4(vPos, 0.0, 1.0);\n"
	"    color = vCol;\n"
	"}\n";

static const char *fragment_shader_text =
	"precision mediump float;\n"
	"varying vec3 color;\n"
	"void main()\n"
	"{\n"
	"    gl_FragColor = vec4(color, 1.0);\n"
	"}\n";

static void error_callback(int error, const char *description)
{
	fprintf(stderr, "Error: %s\n", description);
}
static void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods)
{
	if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS)
		glfwSetWindowShouldClose(window, GLFW_TRUE);
}

std::function<void()> loop;
void main_loop() { loop(); }

void check_error(GLuint shader)
{
	GLint result;
	glGetShaderiv(shader, GL_COMPILE_STATUS, &result);
	if (result == GL_FALSE)
	{
		GLint log_length;
		glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &log_length);
		std::vector<GLchar> log(log_length);

		GLsizei length;
		glGetShaderInfoLog(shader, log.size(), &length, log.data());

		error_callback(0, log.data());
	}
}

int main(void)
{
	GLint mvp_location, vpos_location, vcol_location;
	glfwSetErrorCallback(error_callback);
	if (!glfwInit())
		exit(EXIT_FAILURE);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
	auto window = glfwCreateWindow(640, 480, "Simple example", NULL, NULL);
	if (!window)
	{
		glfwTerminate();
		exit(EXIT_FAILURE);
	}
	glfwSetKeyCallback(window, key_callback);
	glfwMakeContextCurrent(window);
#ifdef __EMSCRIPTEN__
#else
	gladLoadGL();
#endif
	glfwSwapInterval(1);
	// NOTE: OpenGL error checks have been omitted for brevity
	GLuint vertex_buffer;
	glGenBuffers(1, &vertex_buffer);
	glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

	auto vertex_shader = glCreateShader(GL_VERTEX_SHADER);
	glShaderSource(vertex_shader, 1, &vertex_shader_text, NULL);
	glCompileShader(vertex_shader);
	check_error(vertex_shader);

	auto fragment_shader = glCreateShader(GL_FRAGMENT_SHADER);
	glShaderSource(fragment_shader, 1, &fragment_shader_text, NULL);
	glCompileShader(fragment_shader);
	check_error(fragment_shader);

	auto program = glCreateProgram();
	glAttachShader(program, vertex_shader);
	glAttachShader(program, fragment_shader);
	glLinkProgram(program);
	mvp_location = glGetUniformLocation(program, "MVP");
	vpos_location = glGetAttribLocation(program, "vPos");
	vcol_location = glGetAttribLocation(program, "vCol");
	glEnableVertexAttribArray(vpos_location);
	glVertexAttribPointer(vpos_location, 2, GL_FLOAT, GL_FALSE,
						  sizeof(vertices[0]), (void *)0);
	glEnableVertexAttribArray(vcol_location);
	glVertexAttribPointer(vcol_location, 3, GL_FLOAT, GL_FALSE,
						  sizeof(vertices[0]), (void *)(sizeof(float) * 2));

	loop = [&] {
		float ratio;
		int width, height;
		mat4x4 m, p, mvp;
		glfwGetFramebufferSize(window, &width, &height);
		ratio = width / (float)height;
		glViewport(0, 0, width, height);
		glClear(GL_COLOR_BUFFER_BIT);
		mat4x4_identity(m);
		mat4x4_rotate_Z(m, m, (float)glfwGetTime());
		mat4x4_ortho(p, -ratio, ratio, -1.f, 1.f, 1.f, -1.f);
		mat4x4_mul(mvp, p, m);
		glUseProgram(program);
		glUniformMatrix4fv(mvp_location, 1, GL_FALSE, (const GLfloat *)mvp);
		glDrawArrays(GL_TRIANGLES, 0, 3);
		glfwSwapBuffers(window);
		glfwPollEvents();
	};

#ifdef __EMSCRIPTEN__
	emscripten_set_main_loop(main_loop, 0, true);
#else
	while (!glfwWindowShouldClose(window))
		main_loop();
#endif

	glfwDestroyWindow(window);
	glfwTerminate();
	exit(EXIT_SUCCESS);
}

'''


GLFW_HEADER = '''
#ifdef __EMSCRIPTEN__
	#include <emscripten.h>
	#define GL_GLEXT_PROTOTYPES
	#define EGL_EGLEXT_PROTOTYPES
#else
	//#include <glad/glad.h>
	#include <GLES2/gl2.h>
	#include <EGL/egl.h>
	#define EMSCRIPTEN_KEEPALIVE
#endif

#include <GLFW/glfw3.h>
#include "linmath.h"
#include <stdlib.h>
#include <stdio.h>


struct Verts2D{
	float x, y;
	float r, g, b;
};

GLint program;
GLint mvp_location, vpos_location, vcol_location;


'''

GLFW_WIN = '''
GLFWwindow *window;

EMSCRIPTEN_KEEPALIVE
extern void netghost_window_init(int w, int h) {
	if (!glfwInit()) exit(EXIT_FAILURE);

	#ifdef __EMSCRIPTEN__
		glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
		glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
	#else
		glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
		glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
		glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
	#endif


	window = glfwCreateWindow(w, h, "NetGhost", NULL, NULL);
	if (!window) {
		glfwTerminate();
		exit(EXIT_FAILURE);
	}
	glfwMakeContextCurrent(window);
	#ifdef __EMSCRIPTEN__
	#else
//		gladLoadGL();
	#endif
	//glfwSwapInterval(1);
}
'''





GLFW_SHADERS = r'''
static const char *vertex_shader_text =
	"uniform mat4 MVP;\n"
	"attribute vec3 vCol;\n"
	"attribute vec2 vPos;\n"
	"varying vec3 color;\n"
	"void main()\n"
	"{\n"
	"    gl_Position = MVP * vec4(vPos, 0.0, 1.0);\n"
	"    color = vCol;\n"
	"}\n";

static const char *fragment_shader_text =
	"precision mediump float;\n"
	"varying vec3 color;\n"
	"void main()\n"
	"{\n"
	"    gl_FragColor = vec4(color, 1.0);\n"
	"}\n";


EMSCRIPTEN_KEEPALIVE
extern void netghost_init_shaders(){

	GLint vertex_shader = glCreateShader(GL_VERTEX_SHADER);
	glShaderSource(vertex_shader, 1, &vertex_shader_text, NULL);
	glCompileShader(vertex_shader);

	GLint fragment_shader = glCreateShader(GL_FRAGMENT_SHADER);
	glShaderSource(fragment_shader, 1, &fragment_shader_text, NULL);
	glCompileShader(fragment_shader);

	program = glCreateProgram();
	glAttachShader(program, vertex_shader);
	glAttachShader(program, fragment_shader);
	glLinkProgram(program);


	mvp_location = glGetUniformLocation(program, "MVP");
	vpos_location = glGetAttribLocation(program, "vPos");
	vcol_location = glGetAttribLocation(program, "vCol");
	glEnableVertexAttribArray(vpos_location);
	glVertexAttribPointer(vpos_location, 2, GL_FLOAT, GL_FALSE,
						  sizeof(struct Verts2D), (void *)0);
	glEnableVertexAttribArray(vcol_location);
	glVertexAttribPointer(vcol_location, 3, GL_FLOAT, GL_FALSE,
						  sizeof(struct Verts2D), (void *)(sizeof(float) * 2));


}
'''

GLFW_MAIN = r'''
EMSCRIPTEN_KEEPALIVE
int main(){
	printf("enter main\n");
	netghost_window_init(640,480);

	printf("init meshes\n");
	netghost_init_meshes();

	printf("init shaders\n");
	netghost_init_shaders();

	printf("set main loop\n");

	#ifdef __EMSCRIPTEN__
		emscripten_set_main_loop(netghost_redraw, 0, true);
	#else
		while (!glfwWindowShouldClose(window))
			netghost_redraw();
	#endif
}

'''

def build_glfw( gen_ctypes = {}, gen_js = {}):
	if gen_ctypes is not None:
		gen_ctypes['netghost_window_init'] = [ctypes.c_int, ctypes.c_int]

	if gen_js is not None:
		gen_js['netghost_window_init'] = 'function (x,y) {Module.ccall("netghost_window_init", "number", ["number", "number"], [x,y]);}'
		gen_js['netghost_init_meshes'] = 'function () {Module.ccall("netghost_init_meshes", "number", [], []);}'
		gen_js['netghost_redraw'] = 'function () {Module.ccall("netghost_redraw", "number", [], []);}'


	o = [GLFW_HEADER, GLFW_WIN, GLFW_SHADERS]
	helper_funcs = []

	init_meshes = [
		'EMSCRIPTEN_KEEPALIVE',
		'extern void netghost_init_meshes(){',
	]


	draw_loop = [
		'EMSCRIPTEN_KEEPALIVE',
		'extern void netghost_redraw(){',
		#'	printf("redraw...\\n");',
		'	float ratio;',
		'	int width, height;',
		'	mat4x4 matrix, p, mvp;',
		'	glfwGetFramebufferSize(window, &width, &height);',
		'	ratio = width / (float)height;',
		'	glViewport(0, 0, width, height);',
		'	glClearColor(0.07f, 0.13f, 0.17f, 1.0f);',
		'	glClear(GL_COLOR_BUFFER_BIT);',

	]



	blends = []
	shaders = {}
	for arg in sys.argv:
		if arg.endswith((".blend", ".json")):
			blends.append(arg)
		if arg.endswith(".json"):
			## check if there are any shaders
			info = json.loads(open(arg).read())
			if info["shaders"]:
				shaders.update(info["shaders"])


	user_js = []

	if not blends:
		## exports just the default Cube
		blends.append(None)
	for blend in blends:
		if blend and blend.endswith(".json"):
			info = json.loads(open(blend).read())
		else:
			cmd = [BLENDER]
			if blend:
				cmd.append(blend)
			cmd += ["--background", "--python", "./ghostblender.py", "--", "--dump"]
			print(cmd)
			subprocess.check_call(cmd)
			info = json.loads(open("/tmp/dump.json").read())

		shaders.update(info['shaders'])
		if 'javascript' in info and info['javascript']:
			user_js.append(info['javascript'])

		meshes = info["objects"]
		allprops = {}
		for n in meshes:
			if "props" in meshes[n]:
				for k in meshes[n]["props"]:
					if k not in allprops:
						allprops[k] = 1
						draw_loop.append("	float %s;" % k)

		for n in meshes:
			print(meshes[n])
			o.append('GLuint VBO_%s;' % n)
			init_meshes +=[
				'	glGenBuffers(1, &VBO_%s);' % n,
				'	glBindBuffer(GL_ARRAY_BUFFER, VBO_%s);' % n,
				'	glBufferData(GL_ARRAY_BUFFER, sizeof(VERTS_%s), VERTS_%s, GL_STATIC_DRAW);' % (n,n),
			]

			x,y,z = meshes[n]['pos']
			rx,ry,rz = meshes[n]['rot']
			o.append("float transform_%s[6] = {%s,%s,%s, %s,%s,%s};" % (n, x,y,z, rx,ry,rz))

			#verts = ["{%sf,%sf,%sf}" % tuple(vec) for vec in meshes[n]["verts"]]
			#norms = ["{%sf,%sf,%sf}" % tuple(vec) for vec in meshes[n]["normals"]]
			verts = ["{%sf,%sf, %sf,%sf,%sf}" % (vec[0], vec[2], random(), random(), random()) for vec in meshes[n]["verts"]]

			o.append(
				"static const struct Verts2D VERTS_%s[%s] = {%s};"
				% (n, len(verts), ",".join(verts))
			)

			if "props" in meshes[n]:
				for k in meshes[n]["props"]:
					val = meshes[n]["props"][k]
					o.append("float %s_prop_%s = %s;" % (n, k, val))

			helper_funcs += [
				'EMSCRIPTEN_KEEPALIVE',
				'extern void set_%s_pos(float x, float y, float z){' % n,
				'   transform_%s[0]=x;' % n,
				'   transform_%s[1]=y;' % n,
				'   transform_%s[2]=z;' % n,
				'}',
				'EMSCRIPTEN_KEEPALIVE',
				'extern void set_%s_rot(float x, float y, float z){' % n,
				'   transform_%s[3]=x;' % n,
				'   transform_%s[4]=y;' % n,
				'   transform_%s[5]=z;' % n,
				'}',
			]
			if gen_ctypes is not None:
				gen_ctypes['set_%s_pos' % n] = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
				gen_ctypes['set_%s_rot' % n] = [ctypes.c_float, ctypes.c_float, ctypes.c_float]

			if gen_js is not None:
				gen_js['set_%s_pos' % n] = 'function (x,y,z){Module.ccall("set_%s_pos","number", ["number","number","number"],[x,y,z]);}' % n
				gen_js['set_%s_rot' % n] = 'function (x,y,z){Module.ccall("set_%s_rot","number", ["number","number","number"],[x,y,z]);}' % n

			draw_loop += [
				#'	printf("drawing: %s");' % n,
				'	mat4x4_identity(matrix);',
				'	mat4x4_position(matrix, transform_%s[0],transform_%s[1],transform_%s[2]);' %(n,n,n),
				#'	mat4x4_rotate_Z(m, m, (float)glfwGetTime());',
			]

			if "scripts" in meshes[n] and meshes[n]["scripts"]:

				if "props" in meshes[n]:
					for k in meshes[n]["props"]:
						## gets global and sets to local
						draw_loop.append("	%s = %s_prop_%s;" % (k, n, k))


				for cpp in meshes[n]["scripts"]:
					draw_loop.append(cpp)

				if "props" in meshes[n]:
					for k in meshes[n]["props"]:
						## sets global to local
						draw_loop.append("	%s_prop_%s = %s;" % (n, k, k))


			draw_loop += [
				'	mat4x4_ortho(p, -ratio, ratio, -1.f, 1.f, 1.f, -1.f);',
				'	mat4x4_mul(mvp, p, matrix);',

				'	glUseProgram(program);',
				'	glUniformMatrix4fv(mvp_location, 1, GL_FALSE, (const GLfloat *)mvp);',
				'	glBindBuffer(GL_ARRAY_BUFFER, VBO_%s);' % n,
				'	glDrawArrays(GL_TRIANGLES, 0, %s);' % len(verts),

			]


	draw_loop += [
	'	glfwSwapBuffers(window);',
	'	glfwPollEvents();',
	'}'
	]
	init_meshes.append('}')

	o = "\n".join(
		o + helper_funcs + init_meshes + draw_loop + [GLFW_MAIN]
	)
	return o


def gen_js_wrapper( info ):
	js = ['var ghostapi = {']
	for n in info:
		js.append('	%s : %s,' % (n, info[n]))
	js.append('}')
	print('\n'.join(js))
	return '\n'.join(js)

def bind_lib(lib, cdefs):
	for n in cdefs:
		func = getattr(lib, n)
		print('binding %s: args = %s ptr =%s' %(n,cdefs[n], func))
		func.argtypes = tuple(cdefs[n])

def gen_glfw(output='/tmp/test-glfw.so'):
	gctypes = {}
	cpp = build_glfw( gen_ctypes=gctypes )
	print(cpp)
	tmp = '/tmp/test-glfw.c'
	open(tmp, 'w').write(cpp)

	cmd = [
		'gcc', 
		tmp,
		'-shared',
		'-fPIC',
		'-o', output, 
		'-I', _thisdir, 
		'-lGL', '-lGLU',
		'-lGLEW',
		'-lglfw', '-lm',
	]
	print(cmd)
	subprocess.check_call(cmd)

	lib = ctypes.CDLL(output)
	print(lib)
	bind_lib(lib, gctypes)
	print("init_window")
	lib.netghost_window_init(320, 240)

	print("init_meshes")
	lib.netghost_init_meshes()

	print("init_shaders")
	lib.netghost_init_shaders()

	while True:
		print("redraw")
		lib.netghost_redraw()
		#if 'set_Cube_pos' in gctypes:
		#	lib.set_Cube_pos(random(), random(), random())
		time.sleep(1)


def gen_glfw_wasm(output='/tmp/test-glfw.html'):
	gen_js = {}
	cpp = build_glfw( gen_js=gen_js )
	print(cpp)
	tmp = '/tmp/test-glfw.c'
	open(tmp, 'w').write(cpp)


	jslib = '/tmp/ghostlib.js'
	basisu_webgl = os.path.join(_thisdir, 'basis_universal/webgl/texture/')
	assert os.path.isdir(basisu_webgl)
	js = [
		'console.log("ghostnet: post wasm load stage");',
		'console.log("ghostnet: extern C functions: %s");' % ','.join( list(gen_js.keys()) ),
		gen_js_wrapper( gen_js ),
		open(os.path.join(basisu_webgl, 'renderer.js')).read(),
		open(os.path.join(basisu_webgl, 'dxt-to-rgb565.js')).read(),
		'ghostapi.dxtToRgb565 = dxtToRgb565;',
		'ghostapi.basisu_renderer = Renderer;',
	]
	if '__ghostuser__' in gen_js:
		## call user scripts
		js.append('setTimeout(ghostapi.__ghostuser__, 1000);')

	open(jslib, 'w').write( '\n'.join(js) )


	cmd = [
		EMCC, '-o', output, 
		#'--no-entry',
		'-sEXPORTED_RUNTIME_METHODS=ccall,cwrap',
		'--post-js', jslib,
		"-s","FETCH",
		"-s","SINGLE_FILE",
		"-s","ENVIRONMENT=web",
		"-s","WASM=1",
		"-s","AUTO_JS_LIBRARIES",
		"-s","USE_WEBGL2=1",
		"-s","USE_GLFW=3",
		"-s","NO_FILESYSTEM=1",
		'-I', _thisdir, 
		tmp
	]
	print(cmd)
	subprocess.check_call(cmd)

	## this is required because some browsers will not open files in /tmp
	os.system("cp -v %s ~/Desktop/netghost.html" % output)
	webbrowser.open(os.path.expanduser("~/Desktop/netghost.html"))


if __name__ == "__main__":
	if '--test' in sys.argv:
		test_glfw()
	elif '--wasm' in sys.argv:
		gen_glfw_wasm()
	else:
		gen_glfw()
