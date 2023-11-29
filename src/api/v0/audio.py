from microdot_asyncio import Microdot
import hidden_shades
import json

audio_app = Microdot()


def source_response(source):
    return {
        "standardVariables": source.private_variable_manager.info,
        "variables": source.variable_manager.info,
    }


@audio_app.get("")
async def get_audio_info(request):
    hidden_shades.audio_manager.info
    return {
        "sources": {
            "selected": hidden_shades.audio_manager.info["selected"],
            "ids": list(hidden_shades.audio_manager.sources.keys()),
        },
    }


@audio_app.put("/source")
async def put_audio_source(request):
    data = json.loads(request.body.decode())
    hidden_shades.audio_manager.select_source(data["id"])
    return source_response(hidden_shades.audio_manager.audio_source)


@audio_app.get("/source/<id>")
async def get_audio_source(request, id):
    source = hidden_shades.audio_manager.sources[id]
    return source_response(source)


@audio_app.get("/source/<source_id>/variables/<var_id>")
async def get_audio_source_variable(request, source_id, var_id):
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.variable_manager.variables[var_id]
    return variable.get_dict()


@audio_app.put("/source/<source_id>/variables/<var_id>")
async def put_audio_source_variable(request, source_id, var_id):
    data = json.loads(request.body.decode())
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.variable_manager.variables[var_id]
    variable.value = variable.deserialize(data["value"])
    return variable.get_dict()


@audio_app.get("/source/<source_id>/standard_variable/<var_id>")
async def get_audio_source_variable(request, source_id, var_id):
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.private_variable_manager.variables[var_id]
    return variable.get_dict()


@audio_app.put("/source/<source_id>/standard_variable/<var_id>")
async def put_audio_source_variable(request, source_id, var_id):
    data = json.loads(request.body.decode())
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.private_variable_manager.variables[var_id]
    variable.value = variable.deserialize(data["value"])
    return variable.get_dict()
