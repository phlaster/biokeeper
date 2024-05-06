import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, Alert, View, Button, Image ,TextInput } from 'react-native';
import * as Location from 'expo-location';

const getLocationPermission = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') {
    console.log('Permission to access location was denied');
    return false;
  }
  return true;
};

export default function Bio_info({ route, navigation }) {
  const [location, setLocation] = useState(null);

  useEffect(() => {
    const getLocation = async () => {
      const permissionGranted = await getLocationPermission();
      if (permissionGranted) {
        const currentLocation = await Location.getCurrentPositionAsync({});
        setLocation(currentLocation.coords);
      }
    };

    getLocation();
  }, []); // Run only once on component mount

  
  const loadscene = () => {
    // Define the functionality for loadscene
    Alert.alert(
      "Теперь можно сфотографировать местность"
    );
    navigation.navigate('Take_photo');
  };

  const { data } = route.params;
  const [inputValue, setInputValue] = useState(''); 
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        onChangeText={setInputValue} 
        value={inputValue}
        placeholder="Введите что-то"
      />
      <Text>Latitude: {location ? location.latitude : 'Loading...'}</Text>
      <Text>Longitude: {location ? location.longitude : 'Loading...'}</Text>
      <Text>Comment: {inputValue ? inputValue : 'Loading...'}</Text>
      <Text>qr: {data}</Text>
      <Button title={'Начать'} onPress={loadscene} />
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    //backgroundColor: 'purple',
  },
  text: {
    color: 'green',
    marginBottom: 20,
  },
  logo: {
    width: 250,
    height: 250,
  },
  input: {
    height: 40,
    width: '80%',
    borderColor: 'gray',
    borderWidth: 1,
    padding: 10,
    marginBottom: 20,
  },
});
