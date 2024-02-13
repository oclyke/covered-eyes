import React from 'react';

import {
  NativeRouter,
} from 'react-router-native';

import {
  PaperProvider,
  MD3LightTheme as DefaultTheme,
} from 'react-native-paper';

import CitySkiesProvider from 'src/providers/citySkies';
import FavoriteConnectionsProvider from 'src/providers/favoriteConnections';
import PresetsProvider from 'src/providers/presets';
import ColorsProvider from 'src/providers/colors';
import CitySkiesInterface from 'src/lib/citySkies';
import App from 'src/app';

import {
  defaultPresets,
} from 'src/data/presets';

import {
  defaultColors,
} from 'src/data/colors';

const theme = {
  ...DefaultTheme,
};

const instance = new CitySkiesInterface('localhost:1337');

export default function Main() {
  return (
    <NativeRouter>
      <CitySkiesProvider
        instance={instance}
        apiVersion="v0"
      >
        <FavoriteConnectionsProvider
          initial={[
            { name: 'Home', address: '127.0.0.1:1337' },
          ]}
        >
          <PresetsProvider
            initial={defaultPresets}
          >
            <ColorsProvider
              initial={defaultColors}
            >
              <PaperProvider theme={theme}>
                <App />
              </PaperProvider>
            </ColorsProvider>
          </PresetsProvider>
        </FavoriteConnectionsProvider>
      </CitySkiesProvider>
    </NativeRouter>
  );
}
