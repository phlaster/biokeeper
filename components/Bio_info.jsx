import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, Alert, View, Button, Image ,TextInput } from 'react-native';
import * as Location from 'expo-location';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Request from './Requests';

const getLocationPermission = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') {
    console.log('Permission to access location was denied');
    return false;
  }
  return true;
};

const getData = async (key) => {
  try {
    const value = await AsyncStorage.getItem(key);
    if(value !== null) {
      // значение найдено
      return value;
    }
  } catch(e) {
    // ошибка при чтении данных
    console.error("Ошибка при чтении данных", e);
  }
};
const storeData = async (key, value) => {
  try {
    await AsyncStorage.setItem(key, value);
  } catch (e) {
    // сохранение ошибки
    console.error("Ошибка при сохранении данных", e);
  }
};

export default function Bio_info({ route, navigation }) {
  const [location, setLocation] = useState(null);
  const [storedGeoData, setStoredGeoData] = useState('');
  const handleSave = () => {
    
    storeData('GeoData', location);
    
  };
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

  

  const { data } = route.params;
  const loadscene = () => {
    // Define the functionality for loadscene
    Alert.alert(
      "Теперь можно сфотографировать местность"
    );
    
   
    
    navigation.navigate('Take_photo');
  };

  const sendData = () => {
    Requst();
  };

  const [inputValue, setInputValue] = useState(''); 
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        onChangeText={setInputValue} 
        value={inputValue}
        placeholder="Введите название исследования"
      />
      <Text>Latitude: {location ? location.latitude : 'Loading...'}</Text>
      <Text>Longitude: {location ? location.longitude : 'Loading...'}</Text>
      <Text>Comment: {inputValue ? inputValue : 'Loading...'}</Text>
      <Text>qr: {data}</Text>
      <Button title={'Начать'} onPress={loadscene} />
      
      <Button title="Сохранить данные" onPress={handleSave} />
      <Button title="Отправить данные" onPress={sendData} />
      
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
