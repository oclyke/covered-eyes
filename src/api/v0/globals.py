from microdot_asyncio import Microdot
from hidden_shades import globals
import json

globals_app = Microdot()


@globals_app.get("")
async def get_global_variables(request):
    return {
        "variables": globals.variable_manager.info,
    }


@globals_app.get("/variable/<id>")
async def get_global_variable_value(request, id):
    variable = globals.variable_manager.variables[id]
    return variable.get_dict()


@globals_app.put("/variable/<id>")
async def put_global_variable(request, id):
    data = json.loads(request.body.decode())
    variable = globals.variable_manager.variables[id]
    variable.value = variable.deserialize(data["value"])
    return variable.get_dict()
