import React, {
  useState,
} from 'react';

import {
  Button,
  Text,
  TextInput,
  View,
  StyleSheet,
} from 'react-native';

import {
  withSafeHeaderStyles,
} from 'src/components/safeRegions';

import {
  useFavoriteConnectionsApi,
  useFavoriteConnectionsState,
} from 'src/providers/favoriteConnections';

import {
  useInstanceConnection,
} from 'src/hooks/citySkies';

// create a safe header that will bump the content down below the main header
const SafeHeader = withSafeHeaderStyles(View);

const styles = StyleSheet.create({
  error: {
    color: 'red',
  },
  success: {
    color: 'green',
  },
});

function FavoriteConnection({ connection, onConfirm, onRemove }) {
  return (
    <View>
      <Text>{connection.name}</Text>
      <Text>{connection.address}</Text>
      <Button
        title="use"
        onPress={() => {
          if (typeof onConfirm === 'function') {
            onConfirm(connection);
          }
        }}
      />
      <Button
        title="remove"
        onPress={() => {
          if (typeof onConfirm === 'function') {
            onRemove(connection);
          }
        }}
      />
    </View>
  );
}

export default function Connection() {
  const {
    address,
    connected,
    setAddress,
    resetAddress,
  } = useInstanceConnection();
  const {
    add: addFavorite,
    remove: removeFavorite,
  } = useFavoriteConnectionsApi();
  const favorites = useFavoriteConnectionsState();

  // state for text inputs
  const [name, setName] = useState('');
  const [desiredHost, setDesiredHost] = useState('');
  const [desiredPort, setDesiredPort] = useState('');
  const desiredConnection = {
    address: `${desiredHost}:${desiredPort}`,
    name,
  };

  return (
    <>
      <SafeHeader />
      <Text>Connection Page</Text>
      <Text>Connection Status:</Text>
      <Text style={connected ? styles.success : styles.error}>{connected ? 'connected' : 'not connected'}</Text>
      <Text>
        Target Address:
        {address}
      </Text>

      <TextInput
        // style={styles.input}
        placeholder="name"
        value={name}
        onChangeText={setName}
      />

      <TextInput
        // style={styles.input}
        placeholder="hostname"
        value={desiredHost}
        onChangeText={setDesiredHost}
      />

      <TextInput
        // style={styles.input}
        keyboardType="numeric"
        placeholder="port number"
        value={desiredPort}
        onChangeText={setDesiredPort}
      />

      <Button
        title="confirm"
        onPress={() => {
          setAddress(`${desiredHost}:${desiredPort}`);
        }}
      />

      <Button
        title="reset to default"
        onPress={() => resetAddress()}
      />

      <Button
        title="save connection to favorites"
        onPress={() => addFavorite(desiredConnection)}
      />

      {/* show user's favorite connections */}
      <Text>Favorite Connections</Text>
      {favorites.map((connection) => (
        <React.Fragment key={connection.id}>
          <FavoriteConnection
            connection={connection}
            onConfirm={() => {
              setAddress(connection.address);
            }}
            onRemove={() => {
              removeFavorite(connection.id);
            }}
          />
        </React.Fragment>
      ))}
      {favorites.length === 0 && (
        <Text>
          You havent saved any favorite connections yet!
        </Text>
      )}
    </>
  );
}
