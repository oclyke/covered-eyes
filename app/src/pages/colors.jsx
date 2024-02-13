import React from 'react';

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
  useColorsState,
  useColorsApi,
} from 'src/providers/colors';

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
  colorsCard: {
    // width: '100%',
    margin: 10,
    padding: 10,
    flexDirection: 'row',
  },
  colorsCardText: {
    flex: 1,
    justifyContent: 'center',
  },
});

export default function Colors() {
  const colors = useColorsState();
  const [activeStackId] = useInstanceOutputActiveInactiveStacks();
  const [, {
    clearOutputStackLayers,
    bulkAddOutputStackLayers,
  }] = useInstanceApi();
  const {
    remove,
  } = useColorsApi();

  return (
    <ScrollView style={styles.container}>
      <SafeHeader />

      {/* show colors with button to send them to the stack */}
      {Object.keys(colors).map((key) => {
        const colorSequence = colors[key];
        return (
          <React.Fragment key={key}>
            <Surface style={styles.colorsCard}>

              {/* remove color */}
              <Button
                icon="trash-can"
                onPress={() => {
                  remove(key);
                }}
              >
                {/* <Text>Remove</Text> */}
              </Button>

              <View style={styles.colorsCardText}>
                <Text>{colorSequence.name}</Text>
              </View>
              <Button
                icon="check-bold"
                onPress={() => {
                  console.log('add colors layers in bulk', colorSequence);
                  clearOutputStackLayers(activeStackId)
                    .then(() => bulkAddOutputStackLayers(activeStackId, colorSequence.layers))
                    .catch(console.error);
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
