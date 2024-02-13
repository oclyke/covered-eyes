import React from 'react';

import {
  StyleSheet,
  View,
} from 'react-native';

import {
  StatusBar,
} from 'expo-status-bar';

import {
  useTheme,
} from 'react-native-paper';

import {
  Route,
  Routes,
  Outlet,
  Navigate,
} from 'react-router-native';

import {
  useSafeAreaInsets,
} from 'react-native-safe-area-context';

import Connection from 'src/pages/connection';
import Stack from 'src/pages/stack';
import Shards from 'src/pages/shards';
import Layer from 'src/pages/layer';
import Global from 'src/pages/global';
import Presets from 'src/pages/presets';
import Colors from 'src/pages/colors';

import Navigation from 'src/components/navigation';

import {
  withSafeHeaderStyles,
} from 'src/components/safeRegions';

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  main: {
    flex: 1,
    flexDirection: 'column',
    alignItems: 'flex-start',
    justifyContent: 'flex-start',
  },
  header: {
    flexDirection: 'row',
    position: 'absolute',
    width: '100%',
    paddingLeft: 10,
    paddingRight: 10,
  },
  bar: {
    flex: 1,
    borderRadius: '30 30 0 0',
  },
  content: {

  },
  nav: {
    width: '100%',
    position: 'absolute',
  },
});

// create a safe header view that will cover the outlet at the top of the screens
const SafeHeader = withSafeHeaderStyles(View);

/**
 * The global app layout. Provides:
 * - safe area view
 * - global navigation
 *
 * Renders sub-components through outlet.
 *
 * @returns Global layout for the app.
 */
function Layout() {
  const theme = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <View style={styles.container}>
      <StatusBar translucent backgroundColor="transparent" style="light" />

      {/* the main view is allowed to go out of the safe area in top-bottom directions */}
      <View
        style={{
          ...styles.main,
          paddingLeft: insets.left,
          paddingRight: insets.right,
        }}
      >
        <Outlet />
      </View>

      {/* navigation view is outside safe area and positioned back over  */}
      <View
        style={{
          ...styles.nav,
          bottom: insets.bottom,
        }}
      >
        <Navigation />
      </View>

      {/* header is positioned outside the safe area */}
      <SafeHeader style={styles.header}>
        <View
          style={{
            ...styles.bar,
            backgroundColor: theme.colors.primary,
          }}
        />
      </SafeHeader>

    </View>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route path="presets" element={<Presets />} />
        <Route path="colors" element={<Colors />} />
        <Route path="connection" element={<Connection />} />
        <Route path="shards/*" element={<Shards />} />
        <Route path="global" element={<Global />} />
        <Route path="stack/:stackId" element={<Stack />} />
        <Route path="layer/:stackId/:layerId" element={<Layer />} />
      </Route>
      <Route index element={<Navigate replace to="/stack/A" />} />
    </Routes>
  );
}
