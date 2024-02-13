import React from 'react';

import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ScrollView,
} from 'react-native';

import {
  useNavigate,
  useParams,
} from 'react-router-native';

import {
  Button, TextInput,
} from 'react-native-paper';

import {
  LayerViewStack,
} from 'src/components/layer';

import {
  useInstanceOutputStack,
  useInstanceApi,
} from 'src/hooks/citySkies';

import {
  withSafeHeaderStyles,
} from 'src/components/safeRegions';

import {
  getStackLayersSnapshot,
} from 'src/lib/citySkies';

import {
  useCitySkiesState,
} from 'src/providers/citySkies';

import {
  usePresetsApi,
} from 'src/providers/presets';

// create a safe header that will bump the content down below the main header
const SafeHeader = withSafeHeaderStyles(View);

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  controlBar: {
    width: '100%',
    flexDirection: 'row',
    margin: 5,
  },
  layer: {
    margin: 10,
  },
});

/**
 * View a stack from the target.
 * @returns Stack component.
 */
function StackView({ id }) {
  const navigate = useNavigate();
  const [presetName, setPresetName] = React.useState('');
  const [data, loading] = useInstanceOutputStack(id);
  const [, {
    clearOutputStackLayers,
  }] = useInstanceApi();
  const {
    instance,
  } = useCitySkiesState();
  const {
    add: addPreset,
  } = usePresetsApi();

  if (loading === true) {
    return (
      <Text>Loading</Text>
    );
  }

  const {
    // id,
    layers: {
      ids,
    },
  } = data;

  return (
    <>
      <SafeHeader />

      {/* control bar for some operations */}
      <View style={styles.controlBar}>

        <View style={{ flexDirection: 'column', justifyContent: 'space-around' }}>
          <Button
            icon="trash-can"
            onPress={() => {
              clearOutputStackLayers(id)
                .catch(console.error);
            }}
            title="remove all layers"
          />
        </View>

        {/* option for saving preset */}
        <TextInput
          style={{ flex: 1 }}
          value={presetName}
          onChangeText={setPresetName}
          placeholder="Preset Name"
        />
        <View style={{ flexDirection: 'column', justifyContent: 'space-around' }}>
          <Button
            icon="content-save"
            onPress={async () => {
              const layersSnapshot = await getStackLayersSnapshot(instance, id);
              let name = presetName;
              if (name === '') {
                name = `preset-${Date.now()}`;
              }
              addPreset({
                name,
                layers: layersSnapshot,
              });
            }}
          >
            <Text>Save Preset</Text>
          </Button>
        </View>

      </View>

      {/* show layers preview */}
      <ScrollView style={styles.container}>
        {ids.map((layerId) => (
          <React.Fragment key={`layer.${layerId}`}>
            <TouchableOpacity
              onPress={() => {
                navigate(`/layer/${id}/${layerId}`);
              }}
            >
              <View style={styles.layer}>
                <LayerViewStack stackId={id} id={layerId} />
              </View>
            </TouchableOpacity>
          </React.Fragment>
        ))}
      </ScrollView>
    </>
  );
}

export default function Stack() {
  const {
    stackId,
  } = useParams();

  return (
    <StackView id={stackId} />
  );
}
