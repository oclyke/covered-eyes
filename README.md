# covered-eyes

`covered-eyes` presents a dead simple interface to write and compose animations in Python.

**Disclaimer**: Besides being really hackable it's not clear if this project has any real value.
Other tools offer more features, maturity, performance, clarity of intent, or combination thereof.
Check out [alternatives](#better-alternatives) for other runtimes
and [fundamental components](#fundamental-components) for tools that might be useful to integrate directly into a project.

# alternatives

* [ShaderChain](http://connorbell.ca/projects/shaderchain.html) [[sourcehut](https://git.sr.ht/~connorbell/ShaderChain)] – Multi-platform shader composition tool in C++ (MIT).
* [Hedron](https://github.com/nudibranchrecords/hedron) – Perform live shows with three.js (AGPL-3.0).
* [Veda](https://veda.gl/) [[GitHub](https://github.com/fand/veda)] – Atom plugin for VJ live-coding (MIT).
* [ShaderToy](https://www.shadertoy.com/) – Test GLSL shaders in a browser.

# fundamental components

* [pysicgl](https://github.com/oclyke/pysicgl) - Python 2D graphics library that can be used to draw in memory.
* [moderngl](https://github.com/moderngl/moderngl) – Simple interface to OpenGL pipelines.
* [moderngl-window](https://github.com/moderngl/moderngl-window) – Windowing and input handling for moderngl.
* [microdot](https://github.com/miguelgrinberg/microdot) – Small web framework for Python and MicroPython.

# getting started

Starting the runtime begins an animation loop and a REST API server.
If all goes well a window will appear and the [app](#app) can be used to interact with the runtime.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

ln -s ./example-shards ./runtime/persistent/shards_source

python src/main.py
```

# app

Included in the `/app` directory is an Expo project which creates a GUI for manipulating the covered-eyes rest API.

# installing pysicgl from a local copy

```bash
pip install -e ../pysicgl
```

# roadmap

There are a lot of things that need to be done to improve this project.
Here are just a few:

* [ ] remove model logic from the REST API.
* [ ] standardize + document the environment and tools available in layer source code.
* [ ] decouple animation source code form the filesystem.
* [ ] handle caching and version management of animation source code.
* [ ] set an example configuration to avoid black screen on startup.

# ground-up rebuild

When (if) I get back to working on this project I will probably reconsider the entire architecture.

* Strongly versioned API for fragments to interact with the runtime.
  * Fragments declare their API requirements.
  * Runtime tries to satisfy the requirements, or fails to load the fragment.
* Consider support for fragments written in other languages.
(The tricky part, which may prevent this from working, is avoiding serialization of generated data.
Ultimately the fragments need to have some kind of fast inter-process communication.
Presently this is handled using shared memory in the Python runtime.)
* Clearly defined responsibilities of the runtime,
along with the possibility for extensions (which also need a clearly defined API).
* Use Google Protobuf for interface definitions.
* Develop an actual server to host fragments.
(Think of crates.io and their strict reliance on semantic versioning and
disallowing the deletion of versions.)
