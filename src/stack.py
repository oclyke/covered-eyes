import os
from pathutils import rmdirr, ensure_dirs


class Stack:
    @staticmethod
    def layer_id_generator(self):
        """
        This generator gets the next layer id given the path to a dir containing
        layer directories with numeric decimal names in ascending order.
        """
        id = 0
        while True:
            try:
                os.stat(self._layer_path_by_id(id))
                id += 1
            except:
                yield id

    def __init__(self, path_prefix, id, layer_initializer):
        self._id = id
        self._path = f"{path_prefix}{id}"
        self._layers_path = f"{self._path}/layers"
        self._layer_id_generator = Stack.layer_id_generator(self)

        # ensure that a directory exists for layers
        ensure_dirs(self._layers_path)

        # layer map allows access to layers by id while layer stack
        # maintains the order of layers in composition
        self._layer_map = {}
        self._layer_stack = []

        # load layers from the filesystem
        for id in os.listdir(self._layers_path):
            id, path, _ = self.get_layer_info(id)
            print(id, path)
            layer = layer_initializer(id, path)
            self.add_layer(layer)

        # now arrange the layers by index
        self._arrange_layers_by_index()
        self._recompute_layer_indices()

    def __getitem__(self, key):
        return self._layer_stack[key]

    def __len__(self):
        return len(self._layer_stack)

    def _arrange_layers_by_index(self):
        # sort the layers in the stack by index
        self._layer_stack.sort(key=lambda layer: layer.info.get("index"))

    def _recompute_layer_indices(self):
        for idx, layer in enumerate(self._layer_stack):
            layer.set_index(idx)

    def _layer_path_by_id(self, id):
        return f"{self._layers_path}/{id}"

    def get_layer_by_id(self, id):
        return self._layer_map[id]

    def get_layer_info(self, id):
        path = self._layer_path_by_id(id)
        index = len(self._layer_stack)
        return (id, path, index)

    def get_new_layer_info(self):
        id = next(self._layer_id_generator)
        return self.get_layer_info(id)

    def add_layer(self, layer):
        self._layer_stack.append(layer)
        self._layer_map[str(layer.id)] = layer
        self._recompute_layer_indices()

    def move_layer_to_index(self, id, dest_idx):
        original_index = self._layer_map[id].index
        self._layer_stack.insert(dest_idx, self._layer_stack.pop(original_index))
        self._recompute_layer_indices()

    def clear_layers(self):
        """remove all layers"""
        self._layer_stack = []
        self._layer_map = {}
        rmdirr(self._layers_path)
        os.mkdir(self._layers_path)

    def remove_layer_by_id(self, layerid):
        layer = self.get_layer_by_id(layerid)
        layer_index = layer.info.get("index")

        # remove the layer by its index
        self._layer_stack.pop(layer_index)
        self._recompute_layer_indices()

        # remove the layer from the map
        del self._layer_map[layerid]

        # remove storage
        layer.destroy_storage()

    @property
    def id(self):
        return self._id
