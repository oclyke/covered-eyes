from microdot_asyncio import Microdot
import json

from hidden_shades.layer import Layer

output_app = Microdot()


def stack_response(stack):
    layers = list(str(layer.id) for layer in stack)
    return {
        "id": stack.id,
        "layers": {
            "total": len(layers),
            "ids": layers,
        },
    }


def layer_response(layer):
    return {
        "variables": layer.variable_manager.info,
        "standardVariables": layer.private_variable_manager.info,
        "config": layer.info,
    }


def init_output_app(stack_manager, canvas, layer_post_init_hook, globals):
    def add_layer_to_stack(stack, layer_data, canvas, layer_post_init_hook):
        """
        add a layer to the stack
        """
        layer_config = layer_data["config"]
        id, path, index = stack.get_new_layer_info()
        layer = Layer(
            id,
            path,
            canvas,
            globals=globals,
            init_info=layer_config,
            post_init_hook=layer_post_init_hook,
        )
        stack.add_layer(layer)

        # initialize variable values
        try:
            variables = layer_data["variables"]
            for variable_name, variable_value in variables.items():
                variable = layer.variable_manager.variables[variable_name]
                variable.value = variable.deserialize(variable_value)
        except KeyError:
            pass

        # initialize standard variable values
        try:
            standard_variables = layer_data["standardVariables"]
            for variable_name, variable_value in standard_variables.items():
                variable = layer.private_variable_manager.variables[variable_name]
                variable.value = variable.deserialize(variable_value)
        except KeyError:
            pass

        return layer

    @output_app.get("")
    async def get_output_index(request):
        """
        return information about the output state
        """
        return {
            "stacks": {
                "total": 2,
                "ids": list(stack_manager.stacks.keys()),
                "active": stack_manager.info.get("active"),
            },
        }

    @output_app.get("/stack/<stack_id>")
    def get_stack(request, stack_id):
        """
        get information about the stack
        """
        stack = stack_manager.stacks[stack_id]
        return stack_response(stack)

    @output_app.put("/stack/<stack_id>/activate")
    def activate_stack(request, stack_id):
        """
        activate the given stack id
        """
        stack_manager.activate(stack_id)
        stack = stack_manager.stacks[stack_id]
        return stack_response(stack)

    @output_app.delete("/stack/<stack_id>/layers")
    async def delete_stack_layers(request, stack_id):
        """
        remove all layers from the stack
        """
        stack = stack_manager.stacks[stack_id]
        stack.clear_layers()
        return stack_response(stack)

    @output_app.post("/stack/<stack_id>/layers")
    async def add_bulk_stack_layers(request, stack_id):
        """
        add multiple layers to the stack
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        for layer_data in data:
            add_layer_to_stack(stack, layer_data, canvas, layer_post_init_hook)

        return stack_response(stack)

    @output_app.get("/stack/<stack_id>/layer/<layer_id>")
    async def get_layer_info(request, stack_id, layer_id):
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        return layer_response(layer)

    @output_app.post("/stack/<stack_id>/layer")
    async def put_stack_layer(request, stack_id):
        """
        add a layer to the stack
        """
        layer_data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = add_layer_to_stack(stack, layer_data, canvas, layer_post_init_hook)
        return layer_response(layer)

    @output_app.delete("/stack/<stack_id>/layer/<layer_id>")
    async def delete_stack_layer(request, stack_id, layer_id):
        """
        remove a layer from the stack
        """
        stack = stack_manager.stacks[stack_id]
        stack.remove_layer_by_id(str(layer_id))
        return {
            "status": "ok",
        }

    @output_app.put("/stack/<stack_id>/layer/<layer_id>/config")
    async def put_layer_config(request, stack_id, layer_id):
        """
        change the config values of a layer
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        layer.merge_info(data)
        return layer_response(layer)

    @output_app.get("/stack/<stack_id>/layer/<layer_id>/variable/<variable_id>")
    async def get_layer_variable_info(request, stack_id, layer_id, variable_id):
        """
        get variable info
        """
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.variable_manager.variables[variable_id]
        return variable.get_dict()

    @output_app.put("/stack/<stack_id>/layer/<layer_id>/variable/<variable_id>")
    async def put_layer_variable(request, stack_id, layer_id, variable_id):
        """
        set variable value
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.variable_manager.variables[variable_id]
        variable.value = variable.deserialize(data["value"])
        return variable.get_dict()

    @output_app.get(
        "/stack/<stack_id>/layer/<layer_id>/standard_variable/<variable_id>"
    )
    async def get_layer_private_variable_info(request, stack_id, layer_id, variable_id):
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.private_variable_manager.variables[variable_id]
        return variable.get_dict()

    @output_app.put(
        "/stack/<stack_id>/layer/<layer_id>/standard_variable/<variable_id>"
    )
    async def put_layer_private_variable(request, stack_id, layer_id, variable_id):
        """
        set private variable value
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.private_variable_manager.variables[variable_id]
        variable.value = variable.deserialize(data["value"])
        return variable.get_dict()
