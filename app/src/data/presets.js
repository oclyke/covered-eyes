const HomeOnTheRange = {
  name: 'home on the range',
  layers: [
    {
      config: {
        shard_uuid: 'noise',
        use_local_palette: true,
      },
      variables: {
        speed: '0.0001',
        scaleX: '0.04',
        scaleY: '0.04',
      },
      standardVariables: {
        palette: '{"colors": [16090390, 11679195], "map_type": "discrete_circular"}',
      },
    },
    {
      config: {
        shard_uuid: 'diamond',
        use_local_palette: true,
        active: false,
      },
      variables: {
        speed: '0.0001',
        scale: '0.2',
      },
      standardVariables: {
        composition_mode: 'alpha_copy',
      },
    },
  ],
};

const InstantCrush = {
  name: 'Instant Crush',
  layers: [
    {
      config: {
        active: true,
        id: 3,
        index: 0,
        shard_uuid: 'noise',
        use_local_palette: true,
      },
      standardVariables: {
        blending_mode: 'normal',
        brightness: '1.0',
        composition_mode: 'alpha_source_over',
        palette: '{"map_type": "discrete_circular", "colors": [16090390, 11679195]}',
      },
      variables: {
        centerX: '0.0',
        centerY: '0.0',
        offset: '0.0',
        scaleX: '0.04',
        scaleY: '0.04',
        speed: '0.0001',
      },
    },
    {
      config: {
        active: true,
        id: 4,
        index: 1,
        shard_uuid: 'diamond',
        use_local_palette: true,
      },
      standardVariables: {
        blending_mode: 'color_burn',
        brightness: '1.0',
        composition_mode: 'bitwise_or',
        palette: '{"map_type": "continuous_circular", "colors": [0, 16777215]}',
      },
      variables: {
        centerX: '0.0',
        centerY: '0.0',
        eccentricity: '0.0',
        scale: '0.2',
        speed: '0.0001',
      },
    },
  ],
};

export const defaultPresets = [
  HomeOnTheRange,
  InstantCrush,
];
