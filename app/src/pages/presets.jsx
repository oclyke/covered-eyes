import React from 'react';

import {
  useNavigate,
} from 'react-router-native';

import {
  StyleSheet,
  Text,
  ScrollView,
  View,
} from 'react-native';

import {
  Button,
  Surface,
} from 'react-native-paper';

import {
  withSafeHeaderStyles,
  withSafeFooterStyles,
} from 'src/components/safeRegions';

import {
  usePresetsState,
  usePresetsApi,
} from 'src/providers/presets';

import {
  useInstanceOutputActiveInactiveStacks,
  useInstanceApi,
} from 'src/hooks/citySkies';

const SafeHeader = withSafeHeaderStyles(View);
const SafeFooter = withSafeFooterStyles(View);

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  presetCard: {
    // width: '100%',
    margin: 10,
    padding: 10,
    flexDirection: 'row',
  },
  presetCardText: {
    flex: 1,
    justifyContent: 'center',
  },
});

export default function Presets() {
  const presets = usePresetsState();
  const [activeStackId] = useInstanceOutputActiveInactiveStacks();
  const [, {
    clearOutputStackLayers,
    bulkAddOutputStackLayers,
  }] = useInstanceApi();
  const {
    remove,
  } = usePresetsApi();
  const navigate = useNavigate();

  return (
    <ScrollView style={styles.container}>
      <SafeHeader />

      {/* show presets with button to send them to the stack */}
      {Object.keys(presets).map((key) => {
        const preset = presets[key];
        return (
          <React.Fragment key={key}>
            <Surface style={styles.presetCard}>

              <Button
                icon="trash-can"
                onPress={() => {
                  remove(key);
                }}
              >
                {/* <Text>Remove</Text> */}
              </Button>

              <View style={styles.presetCardText}>
                <Text>{preset.name}</Text>
                <Text>{`(${preset.layers.length} layers)`}</Text>
              </View>
              <Button
                icon="check-bold"
                onPress={async () => {
                  await clearOutputStackLayers(activeStackId).catch(console.error);
                  await bulkAddOutputStackLayers(activeStackId, preset.layers).catch(console.error);
                  navigate(`/stack/${activeStackId}`);
                }}
              >
                <Text>Select</Text>
              </Button>
            </Surface>
          </React.Fragment>
        );
      })}

      <SafeFooter />
    </ScrollView>
  );
}
