from microdot_asyncio import Microdot
from semver import SemanticVersion

from .shards import shards_app, init_shards_app
from .output import output_app, init_output_app
from .globals import globals_app
from .audio import audio_app

api_version = SemanticVersion.from_semver("0.0.0")

api_app = Microdot()


def init_api_app(
    stack_manager, canvas, layer_post_init_hook, shards_source_dir, globals
):
    # a sorta ugly way to pass local data into the stacks app...
    init_output_app(stack_manager, canvas, layer_post_init_hook, globals)
    init_shards_app(shards_source_dir)

    api_app.mount(shards_app, url_prefix="/shards")
    api_app.mount(output_app, url_prefix="/output")
    api_app.mount(globals_app, url_prefix="/global")
    api_app.mount(audio_app, url_prefix="/audio")
