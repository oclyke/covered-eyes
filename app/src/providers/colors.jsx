import React, {
  useMemo,
  useState,
  useContext,
  createContext,
  useEffect,
} from 'react';

import AsyncStorage from '@react-native-async-storage/async-storage';

const NO_CONTEXT_ERROR_TEXT = 'No ColorsContext found. Use ColorsProvider.';

const ColorsKey = 'colors';

const ColorsStateContext = createContext(null);
const ColorsApiContext = createContext(null);

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
 * Creates a ColorsApi given a ColorsStateDispatch function.
 * @param {*} setState The dispatch used to change the ColorsState.
 * @returns The ColorsApi.
 */
function ColorsApiFactory(setState, key) {
  /**
   * Clears all colors.
   */
  function clear() {
    setState({});
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
   * Removes a color from storage.
   * @param {*} id The ID of the color to be removed.
   */
  function remove(id) {
    setState((prev) => {
      // use destructuring to excise the removed color
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
 * Provides ConnectionState and ColorsApi to child components
 * @param {*} param0
 * @returns
 */
export default function ColorsProvider({ children, initial }) {
  // state is an object of Colors with a unique ID as the key
  const [state, setState] = useState(initial);

  // read the storage key first
  const key = ColorsKey;
  useEffect(() => {
    AsyncStorage.getItem(key)
      .then((value) => {
        if (value !== null) {
          // an existing value was found - it will be a valid state encoded in JSON
          // parse it and set the state
          setState(JSON.parse(value));
        }
      })
      .catch(console.error);
  }, [key]);

  // memoized API allows API consumers not to re-render on state change
  const api = useMemo(() => ColorsApiFactory(setState, key), [setState, key]);

  return (
    <ColorsStateContext.Provider value={state}>
      <ColorsApiContext.Provider value={api}>
        {children}
      </ColorsApiContext.Provider>
    </ColorsStateContext.Provider>
  );
}

export function useColorsState() {
  const context = useContext(ColorsStateContext);

  if (context === null) {
    throw new Error(NO_CONTEXT_ERROR_TEXT);
  }

  return context;
}

export function useColorsApi() {
  const context = useContext(ColorsApiContext);

  if (context === null) {
    throw new Error(NO_CONTEXT_ERROR_TEXT);
  }

  return context;
}
