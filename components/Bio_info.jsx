import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, Alert, View, Button, Image ,TextInput } from 'react-native';
import * as Location from 'expo-location';
import AsyncStorage from '@react-native-async-storage/async-storage';


const getLocationPermission = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') {
    console.log('Permission to access location was denied');
    return false;
  }
  return true;
};

const storeData = async (value) => {
  try {
    const jsonValue = JSON.stringify(value);
    await AsyncStorage.setItem('my-key', jsonValue);
  } catch (e) {
    console.error('save_error:', error);
  }
};
const getData = async () => {
  try {
    const jsonValue = await AsyncStorage.getItem('my-key');
    return jsonValue != null ? JSON.parse(jsonValue) : null;
  } catch (e) {
    console.error('get_error:', error);
  }
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
      storeData(location);
      data123=getData();
      console.log(data123)
    };

    getLocation();
  }, []); // Run only once on component mount

  const { data } = route.params;
  const loadscene = () => {
    // Define the functionality for loadscene
    Alert.alert(
      "Теперь можно сфотографировать местность"
    );

    //---------------------------------------
    

    
    
    //------------------------------------------
    
    var request = new XMLHttpRequest();
    request.onreadystatechange = (e) => {
      if (request.readyState !== 4) {
        return;
      }
      if (request.status === 200) {
        Alert.alert('success' + request.responseText);
      } else {
        Alert.alert('error' + request.status);
      }
    };
    
    request.open('GET', 'http://62.109.17.249:1337/req/' + "{qr:" + data+"");
    request.send();
    
    navigation.navigate('Take_photo');
  };

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
