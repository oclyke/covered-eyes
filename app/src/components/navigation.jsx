import React from 'react';

import {
  StyleSheet,
  View,
} from 'react-native';

import {
  useNavigate,
} from 'react-router-native';

import {
  Surface,
  Button,
  Text,
} from 'react-native-paper';

import {
  useInstanceConnection,
  useInstanceOutputActiveInactiveStacks,
} from 'src/hooks/citySkies';

const styles = StyleSheet.create({
  surface: {
    height: 50,
    borderRadius: 30,
    marginLeft: 10,
    marginRight: 10,
  },
  vcenter: {
    flex: 1,
    flexDirection: 'column',
    justifyContent: 'center',
  },
  nav: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingRight: 10,
    paddingLeft: 10,
  },
  navButton: {
    flex: 1,
    alignItems: 'center',
  },
  circle: {
    height: 10,
    width: 10,
    borderRadius: '50%',
  },
});

export default function Navigation() {
  const {
    connected,
  } = useInstanceConnection();
  const [activeStackId] = useInstanceOutputActiveInactiveStacks();
  const navigate = useNavigate();

  return (
    <>
      {/* first nav */}
      <Surface elevation={4} style={styles.surface}>
        <View style={styles.vcenter}>
          <View style={styles.nav}>

            {/* presets */}
            <Button
              // mode="outlined"
              style={styles.navButton}
              icon="magic-staff"
              onPress={() => {
                navigate('/presets');
              }}
            >
              <Text>Presets</Text>
            </Button>

            {/* colors */}
            <Button
              // mode="outlined"
              style={styles.navButton}
              icon="select-color"
              onPress={() => {
                navigate('/colors');
              }}
            >
              <Text>Colors</Text>
            </Button>

          </View>
        </View>
      </Surface>

      {/* second nav */}
      <Surface elevation={4} style={styles.surface}>
        <View style={styles.vcenter}>
          <View style={styles.nav}>

            {/* stacks */}
            <Button
              // mode="outlined"
              style={styles.navButton}
              icon="layers-triple"
              onPress={() => {
                navigate(`/stack/${activeStackId}`);
              }}
            >
              <Text>Layers</Text>
            </Button>

            {/* shards */}
            <Button
              // mode="outlined"
              style={styles.navButton}
              icon="layers-plus"
              onPress={() => {
                navigate('/shards');
              }}
            >
              <Text>Shards</Text>
            </Button>

            {/* global */}
            <Button
              // mode="outlined"
              style={styles.navButton}
              icon="globe-model"
              onPress={() => {
                navigate('/global');
              }}
            >
              <Text>Global</Text>
            </Button>

            {/* connection */}
            <Button
              // mode="outlined"
              style={styles.navButton}
              icon="devices"
              onPress={() => {
                navigate('/connection');
              }}
            >
              <Text>Connection</Text>
              <View
                style={{
                  ...styles.circle,
                  backgroundColor: (connected) ? 'green' : 'red',
                }}
              />
            </Button>

          </View>
        </View>
      </Surface>
    </>
  );
}
