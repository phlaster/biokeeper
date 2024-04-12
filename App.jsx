import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text } from 'react-native';
import * as Location from 'expo-location';
import MainStack from './navigate';

const App = () => {
  const [permissionGranted, setPermissionGranted] = useState(false);

  useEffect(() => {
    const getLocationPermission = async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.log('Permission to access location was denied');
        setPermissionGranted(false);
      } else {
        setPermissionGranted(true);
      }
    };

    getLocationPermission();
  }, []); // Run only once on component mount

  if (!permissionGranted) {
    return (
      <View style={styles.container}>
        <Text>Permission to access location was denied</Text>
      </View>
    );
  }

  return <MainStack />;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default App;