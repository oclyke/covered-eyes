class Expression:
    @staticmethod
    def layer_id_generator(path):
        """
        This generator gets the next layer id given the path to a dir containing
        layer directories with numeric integer base10 names in ascending order.
        """
        import os

        id = 0
        while True:
            try:
                os.stat(f"{path}/layers/{id}")
                id += 1
            except:
                yield id

    def __init__(self, path, interface):
        from pathutils import ensure_dirs
        import os

        self._path = path
        self._layers_path = f"{self._path}/layers"
        self._layer_id_generator = Expression.layer_id_generator(self._path)

        # store a reference to the interface that will be passed to layers
        self._interface = interface

        # ensure that a directory exists for layers
        ensure_dirs(self._layers_path)

        # layer map allows access to layers by id while layer stack
        # maintains the order of layers in composition
        self._layer_map = {}
        self._layer_stack = []

        # load layers from the filesystem
        for id in os.listdir(self._layers_path):
            layer = self._make_layer()
            self._layer_map[id] = layer
            self._layer_stack.append(layer)

        # now arrange the layers by index
        self._arrange_layers_by_index()
        self._recompute_layer_indices()

    def _arrange_layers_by_index(self):
        # sort the layers in the stack by index
        self._layer_stack.sort(key=lambda layer: layer.info.get("index"))

    def _recompute_layer_indices(self):
        for idx, layer in enumerate(self._layer_stack):
            layer.info.set("index", idx)

    def _make_layer(
        self,
        path,
    ):
        return Layer(path, self._interface)

    def add_layer(self, shard):
        import os

        id = next(self._layer_id_generator)
        os.mkdir(f"{self._layers_path}/{id}")
        layer = self._make_layer(id)
        layer.info.set("shard", shard)
        self._layer_stack.append(layer)
        self._layer_map[str(id)] = layer
        self._recompute_layer_indices()

    def move_layer_to_index(self, id, dest_idx):
        original_index = self._layer_map[id].index
        self._layer_stack.insert(dest_idx, self._layer_stack.pop(original_index))
        self._recompute_layer_indices()

    def get_layer_index(self, id):
        return self.get_layer_by_id(id).info.get("index")

    def get_layer_by_id(self, id):
        return self._layer_map[id]

    def remove_layer(self, id):
        import os

        os.rmdir(f"{self._layers_path}/{id}")

    def clear_layers(self):
        """remove all layers"""
        self._layer_stack = []
        self._layer_map = {}
        import os
        from pathutils import rmdirr

        rmdirr(self._layers_path)
        os.mkdir(self._layers_path)

    @property
    def layers(self):
        return self._layer_stack
