import React, {
  useMemo,
  useState,
  useContext,
  createContext,
  useEffect,
} from 'react';

import AsyncStorage from '@react-native-async-storage/async-storage';

const NO_CONTEXT_ERROR_TEXT = 'No FavoriteConnectionsContext found. Use FavoriteConnectionsProvider.';

const favoriteConnectionsKey = 'favorite_connections';

const FavoriteConnectionsStateContext = createContext(null);
const FavoriteConnectionsApiContext = createContext(null);

/**
 * Creates an initial state from a list of default items
 * @param {*} defaults
 * @returns initial state
 */
function createStateFromDefaultList(defaults) {
  const favorites = {};
  let nextId = 0;
  defaults.forEach((connection) => {
    favorites[`${nextId}`] = connection;
    nextId += 1;
  });
  return {
    nextId,
    favorites,
  };
}

/**
 * Creates a FavoriteConnectionsApi given a FavoriteConnectionsStateDispatch function.
 * @param {*} setState The dispatch used to change the FavoriteConnectionsState.
 * @returns The ConnectionApi.
 */
function favoriteConnectionsApiFactory(setState, key, initial) {
  /**
   * Clears all favorite connections.
   */
  function clear() {
    const created = createStateFromDefaultList(initial);
    setState(created);
    AsyncStorage.removeItem(key)
      .catch(console.error);
  }

  /**
   * Adds a connection to the favorites.
   * @param {*} connection The connection to add.
   */
  function add(connection) {
    setState((prev) => {
      const updated = {
        favorites: {
          ...prev.favorites,
          [prev.nextId]: connection,
        },
        nextId: prev.nextId + 1,
      };

      // store the update
      AsyncStorage.setItem(key, JSON.stringify(updated))
        .catch(console.error);

      return updated;
    });
  }

  /**
   * Removes a connection from the favorites.
   * @param {*} id The ID of the connection to be removed.
   */
  function remove(id) {
    setState((prev) => {
      // use destructuring to excise the removed connection from the favorites
      const {
        nextId,
        favorites: {
          [id]: removed,
          ...remaining
        },
      } = prev;

      const updated = {
        nextId,
        favorites: remaining,
      };

      // store the update
      AsyncStorage.setItem(key, JSON.stringify(updated))
        .catch(console.error);

      return updated;
    });
  }

  return {
    clear,
    add,
    remove,
  };
}

/**
 * Provides ConnectionState and ConnectionApi to child components
 * @param {*} param0
 * @returns
 */
export default function FavoriteConnectionsProvider({ children, initial }) {
  const [state, setState] = useState({ favorites: {}, nextId: 0 });

  // read the storage key first
  const key = favoriteConnectionsKey;
  useEffect(() => {
    AsyncStorage.getItem(key)
      .then((value) => {
        if (value !== null) {
          // an existing value was found - it will be a valid state encoded in JSON
          // parse it and set the state
          setState(JSON.parse(value));
        } else {
          // create the state from the initial value given and save this in async storage
          const created = createStateFromDefaultList(initial);
          AsyncStorage.setItem(key, JSON.stringify(created))
            .then(() => setState(created))
            .catch(console.error);
        }
      })
      .catch(console.error);
  }, [key]);

  // memoized API allows API consumers not to re-render on state change
  const api = useMemo(
    () => favoriteConnectionsApiFactory(setState, key, initial),
    [setState, key, initial],
  );

  const favorites = useMemo(() => (
    Object.keys(state.favorites).map((id) => ({ id, ...state.favorites[id] }))
  ), [state.favorites]);

  return (
    <FavoriteConnectionsStateContext.Provider value={favorites}>
      <FavoriteConnectionsApiContext.Provider value={api}>
        {children}
      </FavoriteConnectionsApiContext.Provider>
    </FavoriteConnectionsStateContext.Provider>
  );
}

export function useFavoriteConnectionsState() {
  const context = useContext(FavoriteConnectionsStateContext);

  if (context === null) {
    throw new Error(NO_CONTEXT_ERROR_TEXT);
  }

  return context;
}

export function useFavoriteConnectionsApi() {
  const context = useContext(FavoriteConnectionsApiContext);

  if (context === null) {
    throw new Error(NO_CONTEXT_ERROR_TEXT);
  }

  return context;
}
