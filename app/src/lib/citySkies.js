import KVStore from 'src/lib/kvstore';

export default class CitySkiesInstance {
  constructor(address) {
    this.cache = new KVStore();

    this.address = address;
    this.connected = false;
    this.connectionListeners = [];

    // start a ping loop to test the connection state
    this.pingLoop = setInterval(() => {
      const { alive } = this.getApi('static');
      alive()
        .then(() => this.setConnectionState(true))
        .catch(() => this.setConnectionState(false));
    }, 1500);
  }

  /**
   * Subscribes a connection listener.
   * @param {*} listener the listener to subscribe.
   */
  subscribeConnection(listener) {
    this.connectionListeners.push(listener);
  }

  /**
   * Unsubscribes a connection listener.
   * @param {*} listener the listener to unsubscribe.
   */
  unsubscribeConnection(listener) {
    this.connectionListeners = this.connectionListeners.filter((l) => l !== listener);
  }

  /**
   * Notifies all connection listeners of the current connection state.
   */
  notifyConnection() {
    this.connectionListeners.forEach((l) => l({
      connected: this.connected,
      address: this.address,
    }));
  }

  /**
   * Sets the connection state and notifies all listeners.
   * @param {*} connected the new connection state.
   */
  setConnectionState(connected) {
    if (connected === this.connected) {
      // no change
      return;
    }
    this.connected = connected;
    this.notifyConnection();
  }

  /**
   * Sets the address of the instance.
   * @param {*} address the new address of the instance.
   */
  setAddress(address) {
    this.address = address;
  }

  /**
   * Gets the specified api version.
   * @param {*} version the version of the api to get.
   * @returns an object containing the api.
   */
  getApi(version) {
    switch (version) {
      case 'static': return {
        getAlivePath: () => '/alive',
        alive: () => fetch(`http://${this.address}/alive`, { method: 'GET' }),
        getIndexPath: () => '/index',
        index: () => this.get('/index'),
      };
      case 'v0': {
        const prefix = '/api/v0';
        const paths = {
          audio: () => `${prefix}/audio`,
          audioSource: (source) => `${prefix}/audio/source/${source}`,
          audioSourceVariable: (source, variable) => `${prefix}/audio/source/${source}/variable/${variable}`,
          audioSourceStandardVariable: (source, variable) => `${prefix}/audio/source/${source}/standard_variable/${variable}`,
          global: () => `${prefix}/global`,
          globalVariable: (variable) => `${prefix}/global/variable/${variable}`,
          output: () => `${prefix}/output`,
          outputStack: (stack) => `${prefix}/output/stack/${stack}`,
          outputStackActivate: (stack) => `${prefix}/output/stack/${stack}/activate`,
          outputStackLayer: (stack, layer) => `${prefix}/output/stack/${stack}/layer/${layer}`,
          outputStackLayerConfig: (stack, layer) => `${prefix}/output/stack/${stack}/layer/${layer}/config`,
          outputStackLayerVariable: (stack, layer, variable) => `${prefix}/output/stack/${stack}/layer/${layer}/variable/${variable}`,
          outputStackLayerStandardVariable: (stack, layer, variable) => `${prefix}/output/stack/${stack}/layer/${layer}/standard_variable/${variable}`,
        };

        // json fetch helper
        const fetchPathJson = (path, options) => (
          fetch(`http://${this.address}${path}`, options)
            .then((r) => r.text())
            .then((t) => [path, JSON.parse(t)])
        );

        const api = {
          // getters
          getAudio: () => fetchPathJson(paths.audio(), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getAudioSource: (source) => fetchPathJson(paths.audioSource(source), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getAudioSourceVariable: (source, variable) => fetchPathJson(paths.audioSourceVariable(source, variable), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getAudioSourceStandardVariable: (source, variable) => fetchPathJson(paths.audioSourceStandardVariable(source, variable), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getGlobal: () => fetchPathJson(paths.global(), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getGlobalVariable: (variable) => fetchPathJson(paths.globalVariable(variable), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getOutput: () => fetchPathJson(paths.output(), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getOutputStack: (stack) => fetchPathJson(paths.outputStack(stack), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getOutputStackLayer: (stack, layer) => fetchPathJson(paths.outputStackLayer(stack, layer), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getOutputStackLayerConfig: (stack, layer) => fetchPathJson(paths.outputStackLayerConfig(stack, layer), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getOutputStackLayerVariable: (stack, layer, variable) => fetchPathJson(paths.outputStackLayerVariable(stack, layer, variable), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),
          getOutputStackLayerStandardVariable: (stack, layer, variable) => fetchPathJson(paths.outputStackLayerStandardVariable(stack, layer, variable), { method: 'GET' }).then(([path, data]) => this.cache.store(path, data)),

          // setters
          setAudioSourceVariable: (source, variable, value) => (
            fetchPathJson(paths.audioSourceVariable(source, variable), { method: 'PUT', body: JSON.stringify({ value }) })
              .then(async (d) => {
                // update the cached output stack layer data
                fetchPathJson(paths.audioSourceVariable(source, variable), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached audio source variable data', e));
                return d;
              })
          ),
          setAudioSourceStandardVariable: (source, variable, value) => (
            fetchPathJson(paths.audioSourceStandardVariable(source, variable), { method: 'PUT', body: JSON.stringify({ value }) })
              .then(async (d) => {
                // update the cached output stack layer data
                fetchPathJson(paths.audioSourceStandardVariable(source, variable), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached audio source standard variable data', e));
                return d;
              })
          ),
          setGlobalVariable: (variable, value) => (
            fetchPathJson(paths.globalVariable(variable), { method: 'PUT', body: JSON.stringify({ value }) })
          ),
          setOutputStackLayerConfig: (stack, layer, config) => (
            fetchPathJson(paths.outputStackLayerConfig(stack, layer), { method: 'PUT', body: JSON.stringify(config) })
          ),
          setOutputStackLayerVariable: (stack, layer, variable, value) => (
            fetchPathJson(paths.outputStackLayerVariable(stack, layer, variable), { method: 'PUT', body: JSON.stringify({ value }) })
              .then(async (d) => {
                // update the cached output stack layer data
                fetchPathJson(paths.outputStackLayerVariable(stack, layer, variable), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached layer variable data', e));
                return d;
              })
          ),
          setOutputStackLayerStandardVariable: (stack, layer, variable, value) => (
            fetchPathJson(paths.outputStackLayerStandardVariable(stack, layer, variable), { method: 'PUT', body: JSON.stringify({ value }) })
              .then(async (d) => {
                // update the cached output stack layer data
                fetchPathJson(paths.outputStackLayerStandardVariable(stack, layer, variable), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached layer standard variable data', e));
                return d;
              })
          ),

          // deleters
          removeOutputStackLayer: (stack, layer) => (
            fetchPathJson(paths.outputStackLayer(stack, layer), { method: 'DELETE' })
              .then(async (d) => {
                // update the cached output stack data
                fetchPathJson(paths.outputStack(stack), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached output data', e));
                return d;
              })
          ),

          // modifiers
          activateOutputStack: (stack) => (
            fetchPathJson(paths.outputStackActivate(stack), { method: 'PUT', body: JSON.stringify({}) })
          ),
          selectAudioSource: (sourceId) => (
            fetchPathJson(`${paths.audio()}/source`, { method: 'PUT', body: JSON.stringify({ id: sourceId }) })
              .then(async (d) => {
                // update the cached audio data
                fetchPathJson(paths.audio(), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached audio data', e));
                return d;
              })
          ),
          mergeOutputStackLayerConfig: (stack, layer, config) => (
            fetchPathJson(paths.outputStackLayerConfig(stack, layer), { method: 'PUT', body: JSON.stringify(config) })
              .then(async (d) => {
                // update the cached output stack data
                fetchPathJson(paths.outputStackLayer(stack, layer), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached layer data', e));
                return d;
              })
          ),
          addOutputStackLayer: (stack, config) => (
            fetchPathJson(`${paths.outputStack(stack)}/layer`, { method: 'POST', body: JSON.stringify(config) })
              .then(async (d) => {
                // update the cached output stack data
                fetchPathJson(paths.outputStack(stack), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached output data', e));
                return d;
              })
          ),
          clearOutputStackLayers: (stack) => (
            fetchPathJson(`${paths.outputStack(stack)}/layers`, { method: 'DELETE' })
              .then(async (d) => {
                // update the cached output stack data
                fetchPathJson(paths.outputStack(stack), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached output data', e));
                return d;
              })
          ),
          bulkAddOutputStackLayers: (stack, layersData) => (
            fetchPathJson(`${paths.outputStack(stack)}/layers`, { method: 'POST', body: JSON.stringify(layersData) })
              .then(async (d) => {
                // update the cached output stack data
                fetchPathJson(paths.outputStack(stack), { method: 'GET' })
                  .then(([path, data]) => this.cache.store(path, data))
                  .catch((e) => console.error('error updating the cached output data', e));
                return d;
              })
          ),
        };

        return api;
      }
      default: throw new Error('invalid api version');
    }
  }
}

/**
 * Gets a snapshot of the specified stack from the instance.
 *
 * A snapshot is an array of layers, each with the layer configuration,
 * variables, and standard variables.
 *
 * This function gets the data from the cache directly.
 *
 * @param {*} instance
 * @param {*} stack_id
 */
export async function getStackLayersSnapshot(instance, stackId) {
  const api = instance.getApi('v0');
  const [, stack] = await api.getOutputStack(stackId);
  const layerIds = stack.layers.ids;
  const numLayers = layerIds.length;

  // get the data for each layer
  const layers = [];
  for (let idx = 0; idx < numLayers; idx += 1) {
    const layerId = layerIds[idx];

    // eslint-disable-next-line no-await-in-loop
    const [, data] = await api.getOutputStackLayer(stackId, layerId);
    const {
      config,
      variables: {
        ids: variableIds,
      },
      standardVariables: {
        ids: standardVariableIds,
      },
    } = data;

    // eslint-disable-next-line no-await-in-loop
    const variableInfos = await Promise.all(
      variableIds.map((variableId) => (
        api.getOutputStackLayerVariable(stackId, layerId, variableId))),
    );
    const variables = variableInfos.reduce((acc, [, info]) => {
      const {
        id,
        value,
      } = info;
      acc[id] = value;
      return acc;
    }, {});

    // eslint-disable-next-line no-await-in-loop
    const standardVariableInfos = await Promise.all(
      standardVariableIds.map((variableId) => (
        api.getOutputStackLayerStandardVariable(stackId, layerId, variableId)
      )),
    );
    const standardVariables = standardVariableInfos.reduce((acc, [, info]) => {
      const {
        id,
        value,
      } = info;
      acc[id] = value;
      return acc;
    }, {});

    const layer = {
      config,
      variables,
      standardVariables,
    };

    layers.push(layer);
  }

  return layers;
}
