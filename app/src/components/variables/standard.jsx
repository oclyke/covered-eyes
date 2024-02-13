import React, {
  useEffect,
  useState,
} from 'react';

import {
  View,
  TextInput as NativeTextInput,
} from 'react-native';

import {
  Text,
  RadioButton,
  Button,
  Switch,
  TextInput,
} from 'react-native-paper';

import Slider from '@react-native-community/slider';

import ColorConvert from 'color-convert';

// eslint-disable-next-line no-unused-vars
function GenericVariable({ info, onChange }) {
  const {
    description,
    id,
    typecode,
    value,
  } = info;

  return (
    <View>
      <Text>Unknown variable type!</Text>
      <Text>{`Name: ${id}`}</Text>
      <Text>{`Value: ${value}`}</Text>
      <Text>{`Typecode: ${typecode}`}</Text>
      <Text>{`Description: ${description}`}</Text>
    </View>
  );
}

function BooleanVariable({ info, onChange }) {
  const {
    data: {
      tags,
    },
    value: stringValue,
  } = info;

  const value = (stringValue === 'True');

  const [off, on] = tags;

  return (
    <View>
      <View style={{ flexDirection: 'row' }}>

        <Text>{off}</Text>
        <Switch
          value={value}
          onValueChange={() => {
            onChange((value) ? 'False' : 'True');
          }}
        />
        <Text>{on}</Text>

      </View>

    </View>
  );
}

function IntegerVariable({ info, onChange }) {
  const [minText, setMinText] = useState('');
  const [maxText, setMaxText] = useState('');

  const {
    data: {
      default_range: defaultRange,
      allowed_range: allowedRange,
    },
    value,
  } = info;

  let [min, max] = defaultRange;
  if (minText !== '') { min = parseInt(minText, 10); }
  if (maxText !== '') { max = parseInt(maxText, 10); }
  if (min > max) { [min, max] = [max, min]; }

  if ((typeof allowedRange !== 'undefined')
    && (allowedRange !== null)
    && (allowedRange.length === 2)) {
    const [minAllowed, maxAllowed] = allowedRange;
    if (min < minAllowed) { min = minAllowed; }
    if (max > maxAllowed) { max = maxAllowed; }
  }

  return (
    <View>

      <View style={{ flexDirection: 'row' }}>
        <View style={{ flex: 1 }}>
          <NativeTextInput
            label="Min"
            value={minText}
            onChangeText={setMinText}
            placeholder="min value"
          />
        </View>
        <View style={{ flex: 1 }}>
          <NativeTextInput
            label="Max"
            value={maxText}
            onChangeText={setMaxText}
            placeholder="max value placeholder"
          />
        </View>
      </View>

      <Text>{`[${min}, ${max}]: ${value}`}</Text>
      <Slider
        value={parseInt(value, 10)}
        minimumValue={min}
        maximumValue={max}
        onSlidingComplete={(val) => {
          let updated = val;
          if (val < min) { updated = min; }
          if (val > max) { updated = max; }
          onChange(`${Math.round(updated)}`);
        }}
      />

    </View>
  );
}

function FloatingVariable({ info, onChange }) {
  const [minText, setMinText] = useState('');
  const [maxText, setMaxText] = useState('');

  const {
    data: {
      default_range: defaultRange,
      allowed_range: allowedRange,
    },
    value,
  } = info;

  let [min, max] = defaultRange;
  if (minText !== '') {
    const result = parseFloat(minText);
    if (!Number.isNaN(result)) { min = result; }
  }
  if (maxText !== '') {
    const result = parseFloat(maxText);
    if (!Number.isNaN(result)) { max = result; }
  }
  if (min > max) { [min, max] = [max, min]; }

  if ((typeof allowedRange !== 'undefined')
    && (allowedRange !== null)
    && (allowedRange.length === 2)) {
    const [minAllowed, maxAllowed] = allowedRange;
    if (min < minAllowed) { min = minAllowed; }
    if (max > maxAllowed) { max = maxAllowed; }
  }

  return (
    <View>

      <View style={{ flexDirection: 'row' }}>
        <View style={{ flex: 1 }}>
          <NativeTextInput
            label="Min"
            value={minText}
            onChangeText={setMinText}
            placeholder="min value"
          />
        </View>
        <View style={{ flex: 1 }}>
          <NativeTextInput
            label="Max"
            value={maxText}
            onChangeText={setMaxText}
            placeholder="max value placeholder"
          />
        </View>
      </View>

      <Text>{`[${min}, ${max}]: ${value}`}</Text>

      <Slider
        value={parseFloat(value)}
        minimumValue={min}
        maximumValue={max}
        onSlidingComplete={(val) => {
          let updated = val;
          if (val < min) { updated = min; }
          if (val > max) { updated = max; }
          onChange(`${updated}`);
        }}
      />

    </View>
  );
}

function OptionVariable({ info, onChange }) {
  const {
    data: {
      options,
    },
    value,
  } = info;

  return (
    <View>

      {options.map((option) => (
        <React.Fragment key={option}>
          <View style={{ flexDirection: 'row' }}>
            <Text>{option}</Text>
            <RadioButton
              value={option}
              status={(value === option) ? 'checked' : 'unchecked'}
              onPress={() => onChange(option)}
            />
          </View>
        </React.Fragment>
      ))}

    </View>
  );
}

function getColorStrings(colors) {
  return colors.map((color) => [
    // eslint-disable-next-line no-bitwise
    (color & 0xff0000) >> 16,
    // eslint-disable-next-line no-bitwise
    (color & 0x00ff00) >> 8,
    // eslint-disable-next-line no-bitwise
    (color & 0x0000ff) >> 0,
  ]).map((rgb) => `#${ColorConvert.rgb.hex(rgb)}`);
}

function intToHexString(int) {
  let hex = int.toString(16);
  while (hex.length < 6) {
    hex = `0${hex}`;
  }
  return hex;
}

function isHexColor(text) {
  const result = parseInt(text, 16);
  if (Number.isNaN(result)) {
    return false;
  }
  return true;
}

function ColorPaletteVariable({ info, onChange }) {
  function createUpdate(text, type) {
    // parse colors
    const nodes = text
      .split('#')
      .map((node) => node.trim())
      .filter((node) => node !== '');

    const colors = nodes
      .filter((node) => (node.length >= 6 && node.length <= 8))
      .filter((node) => isHexColor(node))
      .map((node) => parseInt(node, 16));

    const data = {
      colors,
      interpolator: type,
    };

    return data;
  }

  const initialInput = `#${JSON.parse(info.value).colors.map((color) => intToHexString(color)).join('#')}`;
  const mapType = JSON.parse(info.value).interpolator;
  const [input, setInput] = useState(initialInput);
  const [update, setUpdate] = useState(createUpdate(input, mapType));

  const {
    value,
  } = info;

  console.log('value', value);

  // convert string value into JSON
  const {
    colors,
  } = JSON.parse(value);

  // convert colors to hex strings
  const colorsStrings = getColorStrings(colors);

  return (
    <View>
      <TextInput
        value={input}
        onChangeText={(text) => {
          setInput(text);
          const data = createUpdate(text, mapType);
          setUpdate(data);
        }}
        placeholder="color palette: '#fcba03 #xx03e7fc #6f03fc'"
      />

      <View style={{ display: 'flex', flexDirection: 'row' }}>
        {colorsStrings.map((color, idx) => (
          <React.Fragment key={idx}>
            <View
              style={{
                backgroundColor: color,
                width: `${100 / colorsStrings.length}%`,
                height: 20,
              }}
            />
          </React.Fragment>
        ))}
      </View>

      <Text />
      {/* buttons to create map types */}
      {[
        'CONTINUOUS_CIRCULAR',
        'DISCRETE_CIRCULAR',
        'CONTINUOUS_LINEAR',
        'DISCRETE_LINEAR',
      ].map((type) => (
        <React.Fragment key={type}>
          <View style={{ flexDirection: 'row' }}>
            <Text>{type}</Text>
            <RadioButton
              value={type}
              status={(mapType === type) ? 'checked' : 'unchecked'}
              onPress={() => {
                const data = createUpdate(input, type);
                setUpdate(data);
                onChange(JSON.stringify(data));
              }}
            />
          </View>
        </React.Fragment>
      ))}

      <Button
        onPress={() => {
          onChange(JSON.stringify(update));
        }}
      >
        <Text>Submit</Text>
      </Button>

    </View>
  );
}

function StringVariable({ info, onChange }) {
  const [text, setText] = useState('');
  const {
    id,
    value,
  } = info;

  // update text when value changes
  useEffect(() => {
    setText(value);
  }, [value]);

  return (
    <View>

      <TextInput
        label={id}
        value={text}
        onChangeText={(value) => { setText(value); }}
      />

      <Button
        onPress={() => {
          onChange(text);
          setText(text);
        }}
        // icon="backup-restore"
      >
        <Text>Submit</Text>
      </Button>

    </View>
  );
}

function getSpecializedVariable(typecode) {
  switch (typecode) {
    case 1: return BooleanVariable;
    case 2: return IntegerVariable;
    case 3: return FloatingVariable;
    case 4: return OptionVariable;
    case 5: return ColorPaletteVariable;
    case 6: return StringVariable;
    default: return GenericVariable;
  }
}

/**
 * Renders variable info from the target at path.
 * @param {
 *  info: the variable info to render
 * }
 * @returns
 */
export function Variable({ info, onChange }) {
  const {
    typecode,
    id,
    description,
    default: defaultValue,
  } = info;
  const SpecializedVariable = getSpecializedVariable(typecode);

  function handleChange(value) {
    onChange?.(value);
  }

  return (
    <>
      <Text variant="titleMedium">{id}</Text>
      <Text>{description}</Text>
      <SpecializedVariable info={info} onChange={(value) => { handleChange(value); }} />
      <Button
        onPress={() => handleChange(defaultValue)}
        icon="backup-restore"
      />
    </>
  );
}
