import {
  useMemo,
  useState,
  useEffect,
} from 'react';

import {
  useCitySkiesState,
  useCitySkiesApi,
} from 'src/providers/citySkies';

export function useInstanceApi() {
  return useCitySkiesApi();
}

export function useInstanceConnection() {
  const {
    instance,
    defaultAddress,
  } = useCitySkiesState();
  const [state, setState] = useState({
    connected: instance.connected,
    address: instance.address,
  });

  const api = useMemo(() => ({
    setAddress: (addr) => {
      setState((prev) => ({ ...prev, address: addr }));
      instance.setAddress(addr);
    },
    resetAddress: () => {
      setState((prev) => ({ ...prev, address: defaultAddress }));
      instance.setAddress(defaultAddress);
    },
  }), [defaultAddress]);

  // subscribe to connection state changes
  // when the instance state changes, update the local state
  useEffect(() => {
    function listener(status) {
      setState(status);
    }
    instance.subscribeConnection(listener);
    return function cleanup() {
      instance.unsubscribeConnection(listener);
    };
  }, []);

  return {
    address: state.address,
    connected: state.connected,
    setAddress: api.setAddress,
    resetAddress: api.resetAddress,
  };
}

export function useInstanceData(get, ...args) {
  const { instance } = useCitySkiesState();
  const [path, setPath] = useState(null);
  const [data, setData] = useState();

  // kick off the initial data fetch
  // this will set the path and data
  // after the path is updated we will have access to the cache
  useEffect(() => {
    get(...args)
      .then(([p, d]) => {
        setData(d);
        setPath(p);
      })
      .catch(console.error);
  }, [get, ...args]);

  // subscribe to the cache and get initial data
  // when the path becomes known we can add a subscription to the cache
  useEffect(() => {
    if (path === null) {
      // when the path is null do not subscribe
      return () => {};
    }

    // the listener will update the state when the cache changes
    // the cache will be updated by the api
    function listener(key, value) {
      console.log('the cache changed!', key, value);
      setData(value);
    }
    instance.cache.subscribe(path, listener);

    // return a cleanup function that unsubscribes from the cache
    return function cleanup() {
      instance.cache.unsubscribe(path, listener);
    };
  }, [path]);

  // determine whether the data has been loaded
  const loading = (path === null);

  // return the state and loading status
  return [data, loading];
}

export function useInstanceGlobal() {
  const [, {
    getGlobal,
  }] = useCitySkiesApi();
  const state = useInstanceData(getGlobal);
  return state;
}

export function useInstanceGlobalVariable(variableId) {
  const [, {
    getGlobalVariable,
  }] = useCitySkiesApi();
  const state = useInstanceData(getGlobalVariable, variableId);
  return state;
}

export function useInstanceAudio() {
  const [, {
    getAudio,
  }] = useCitySkiesApi();
  const state = useInstanceData(getAudio);
  return state;
}

export function useInstanceAudioSource(sourceId) {
  const [, {
    getAudioSource,
  }] = useCitySkiesApi();
  const state = useInstanceData(getAudioSource, sourceId);
  return state;
}

export function useInstanceAudioSourceStandardVariable(sourceId, layerId) {
  const [, {
    getAudioSourceStandardVariable,
  }] = useCitySkiesApi();
  const state = useInstanceData(getAudioSourceStandardVariable, sourceId, layerId);
  return state;
}

export function useInstanceAudioSourceVariable(sourceId, variableId) {
  const [, {
    getAudioSourceVariable,
  }] = useCitySkiesApi();
  const state = useInstanceData(getAudioSourceVariable, sourceId, variableId);
  return state;
}

/**
 * Hook for output data from the instance.
 * @returns the output data and loading status from useInstanceData.
 */
export function useInstanceOutput() {
  const [, {
    getOutput,
  }] = useCitySkiesApi();
  const state = useInstanceData(getOutput);
  return state;
}

export function useInstanceOutputActiveInactiveStacks() {
  const [data, loading] = useInstanceOutput();
  let active = 'A';
  let inactive = 'B';
  if (loading === false) {
    active = data.stacks.active;
    inactive = (active === 'A') ? 'B' : 'A';
  }
  return [active, inactive];
}

/**
 * Hook for output stack data from the instance.
 * @param {*} stackId the id of the stack to get.
 * @returns the output data and loading status from useInstanceData.
 */
export function useInstanceOutputStack(stackId) {
  const [, {
    getOutputStack,
  }] = useCitySkiesApi();
  const state = useInstanceData(getOutputStack, stackId);
  return state;
}

export function useInstanceOutputStackLayer(stackId, layerId) {
  const [, {
    getOutputStackLayer,
  }] = useCitySkiesApi();
  const state = useInstanceData(getOutputStackLayer, stackId, layerId);
  return state;
}

export function useInstanceOutputStackLayerVariable(stackId, layerId, variableId) {
  const [, {
    getOutputStackLayerVariable,
  }] = useCitySkiesApi();
  const state = useInstanceData(getOutputStackLayerVariable, stackId, layerId, variableId);
  return state;
}

export function useInstanceOutputStackLayerStandardVariable(stackId, layerId, variableId) {
  const [, {
    getOutputStackLayerStandardVariable,
  }] = useCitySkiesApi();
  const state = useInstanceData(getOutputStackLayerStandardVariable, stackId, layerId, variableId);
  return state;
}
