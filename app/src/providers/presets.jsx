import React, {
  useMemo,
  useState,
  useContext,
  createContext,
  useEffect,
} from 'react';

import AsyncStorage from '@react-native-async-storage/async-storage';

const NO_CONTEXT_ERROR_TEXT = 'No PresetsContext found. Use PresetsProvider.';

const presetsKey = 'presets';

const PresetsStateContext = createContext(null);
const PresetsApiContext = createContext(null);

/**
 * Gets a unique ID for a preset in the given state.
 * @param {*} state: The state to check for uniqueness.
 * @returns A unique ID.
 */
function getNewId(state) {
  let nextId = 0;
  while (true) {
    const id = `${nextId}`;
    if (!(id in state)) {
      return id;
    }
    nextId += 1;
  }
}

/**
 * Creates an initial state from a list of default items
 * @param {*} defaults: The list of default items.
 * @returns initial state
 */
function createStateFromInitialList(initialList) {
  const state = {};
  initialList.forEach((preset) => {
    const id = getNewId(state);
    console.log('creating initial preset: ', preset, id);
    state[id] = preset;
  });
  return state;
}

/**
 * Creates a PresetsApi given a PresetsStateDispatch function.
 * @param {*} setState The dispatch used to change the PresetsState.
 * @returns The PresetsApi.
 */
function PresetsApiFactory(setState, key, initial) {
  /**
   * Clears all presets.
   */
  function clear() {
    const created = createStateFromInitialList(initial);
    setState(created);
    AsyncStorage.removeItem(key)
      .catch(console.error);
  }

  /**
   * Stores a preset.
   * @param {*} preset The preset to add.
   */
  function add(preset) {
    setState((prev) => {
      // get a unique id to store the preset
      const id = getNewId(prev);
      const updated = {
        ...prev,
        [id]: preset,
      };

      // store the update
      AsyncStorage.setItem(key, JSON.stringify(updated))
        .catch(console.error);

      return updated;
    });
  }

  /**
   * Removes a preset from storage.
   * @param {*} id The ID of the connection to be removed.
   */
  function remove(id) {
    setState((prev) => {
      // use destructuring to excise the removed preset
      const {
        [id]: removed,
        ...remaining
      } = prev;

      // store the update
      AsyncStorage.setItem(key, JSON.stringify(remaining))
        .catch(console.error);

      return remaining;
    });
  }

  return {
    clear,
    add,
    remove,
  };
}

/**
 * Provides ConnectionState and PresetsApi to child components
 * @param {*} param0
 * @returns
 */
export default function PresetsProvider({ children, initial }) {
  // state is an object of presets with a unique ID as the key
  const [state, setState] = useState({});

  // read the storage key first
  const key = presetsKey;
  useEffect(() => {
    AsyncStorage.getItem(key)
      .then((value) => {
        if (value !== null) {
          // an existing value was found - it will be a valid state encoded in JSON
          // parse it and set the state
          setState(JSON.parse(value));
        } else {
          // create the state from the initial value given and save this in async storage
          const created = createStateFromInitialList(initial);
          AsyncStorage.setItem(key, JSON.stringify(created))
            .then(() => setState(created))
            .catch(console.error);
        }
      })
      .catch(console.error);
  }, [key]);

  // memoized API allows API consumers not to re-render on state change
  const api = useMemo(() => PresetsApiFactory(setState, key, initial), [setState, key, initial]);

  return (
    <PresetsStateContext.Provider value={state}>
      <PresetsApiContext.Provider value={api}>
        {children}
      </PresetsApiContext.Provider>
    </PresetsStateContext.Provider>
  );
}

export function usePresetsState() {
  const context = useContext(PresetsStateContext);

  if (context === null) {
    throw new Error(NO_CONTEXT_ERROR_TEXT);
  }

  return context;
}

export function usePresetsApi() {
  const context = useContext(PresetsApiContext);

  if (context === null) {
    throw new Error(NO_CONTEXT_ERROR_TEXT);
  }

  return context;
}
