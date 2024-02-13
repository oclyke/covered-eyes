import React from 'react';

import {
  StyleSheet,
  View,
} from 'react-native';

import {
  Surface,
  Button,
  Text,
  Switch,
  useTheme,
} from 'react-native-paper';

import {
  useInstanceApi,
  useInstanceOutputStackLayer,
} from 'src/hooks/citySkies';

const styles = StyleSheet.create({
  surface: {
    borderRadius: 10,
    padding: 5,
  },
});

export function LayerConfig({ config }) {
  const {
    active,
    id,
    index,
    shard_uuid: shardId,
    use_local_palette: useLocalPalette,
  } = config;

  return (
    <View>
      <Text>Info:</Text>
      <Text>{`shard: ${shardId}`}</Text>
      <Text>{`id: ${id}`}</Text>
      <Text>{`index: ${index}`}</Text>
      <Text>{`active: ${active}`}</Text>
      <Text>{`local palette: ${useLocalPalette}`}</Text>
    </View>
  );
}

export function LayerViewStack({ stackId, id }) {
  const theme = useTheme();
  const [, {
    removeOutputStackLayer,
    mergeOutputStackLayerConfig,
  }] = useInstanceApi();
  const [data, loading] = useInstanceOutputStackLayer(stackId, id);

  if (loading === true) {
    return (
      <Text>Loading</Text>
    );
  }

  const {
    config: {
      active,
      use_local_palette: useLocalPalette,
      shard_uuid: shardId,
    },
  } = data;

  // create dynamic style to indicate whether the layer is active
  const dynamicStyle = {};
  if (active === false) {
    dynamicStyle.backgroundColor = theme.colors.tertiary;
  }

  return (
    <Surface elevation={2} style={{ ...styles.surface, ...dynamicStyle }}>

      {/* allow for two columns */}
      <View style={{ flexDirection: 'row' }}>

        {/* column 1 */}
        <View style={{ flexDirection: 'column', flexGrow: 1 }}>
          <Text>{shardId}</Text>
        </View>

        {/* column 2 */}
        <View style={{ flexDirection: 'column', height: '100%' }}>
          <View style={{ flexDirection: 'row' }}>

            <Switch
              value={active}
              onValueChange={() => {
                mergeOutputStackLayerConfig(stackId, id, { active: !active })
                  .catch(console.error);
              }}
            />

            <Switch
              value={useLocalPalette}
              onValueChange={() => {
                mergeOutputStackLayerConfig(stackId, id, { use_local_palette: !useLocalPalette })
                  .catch(console.error);
              }}
            />

            <Button
              icon="delete"
              onPress={() => {
                removeOutputStackLayer(stackId, id)
                  .catch(console.error);
              }}
            />

          </View>
        </View>
      </View>
    </Surface>
  );
}
