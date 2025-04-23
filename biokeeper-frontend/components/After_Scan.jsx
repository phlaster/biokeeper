import React, { useState, useEffect } from 'react';
import { View, FlatList } from 'react-native';
import { Surface, Text, Button, IconButton } from 'react-native-paper';
import * as Location from 'expo-location';

import styles from '../styles/style';

const getLocationPermission = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();
  return status === 'granted';
};

const getCurrentLocation = async () => {
  const { coords } = await Location.getCurrentPositionAsync({});
  return coords;
};

export default function After_Scan({ route, navigation }) {
  const [location, setLocation] = useState(null);
  const [timestamp] = useState(new Date());
  const { data } = route.params;

  useEffect(() => {
    const fetchLocation = async () => {
      const permissionGranted = await getLocationPermission();
      if (permissionGranted) {
        setLocation(await getCurrentLocation());
      }
    };

    fetchLocation();
  }, []);

  const handleSave = () => {
    // Currently does nothing
    console.log('Save button pressed');
  };

  const handleCancel = () => {
    navigation.navigate('LK');
  };

  const formatTimestamp = (date) => {
    const pad = (num) => num.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  };

  const dataItems = [
    { label: 'QR', value: data, icon: null },
    { label: 'Time', value: formatTimestamp(timestamp), icon: null },
    { label: 'GPS', value: location ? `${location.latitude.toFixed(5)}, ${location.longitude.toFixed(5)}` : 'Loading...', icon: null },
    { label: 'Comment', value: '', icon: <IconButton icon="plus" size={24} onPress={() => console.log('Add comment pressed')} style={styles.addInfoButton} /> },
    { label: 'Photo', value: '', icon: <IconButton icon="camera" size={24} onPress={() => console.log('Add photo pressed')} style={styles.addInfoButton} /> },
  ];

  const renderItem = ({ item }) => (
    <View style={[styles.dataRow, { height: 30 }]}>
      <Text style={[styles.dataLabel, { width: 80, textAlign: 'right' }]}>{item.label}:</Text>
      <Text style={[styles.dataValue, { flex: 1, marginRight: 10 }]} numberOfLines={1} ellipsizeMode="tail">{item.value.length > 25 ? item.value.substring(0, 25) + '...' : item.value}</Text>
      {item.icon}
    </View>
  );

  return (
    <View style={styles.container}>
      <Surface style={styles.scanDataSurface}>
        <FlatList
          data={dataItems}
          renderItem={renderItem}
          keyExtractor={(item, index) => index.toString()}
        />
      </Surface>
      <View style={styles.buttonContainer}>
        <Button
          mode="outlined"
          onPress={handleCancel}
          style={styles.button}
        >
          Cancel
        </Button>
        <Button
          mode="contained"
          onPress={handleSave}
          style={styles.button}
        >
          Save
        </Button>
      </View>
    </View>
  );
}