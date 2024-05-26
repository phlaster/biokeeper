import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button,TextInput} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

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


export default function Autorization({navigation}) {
const loadscene=()=>{
  storeData('login', inputLogin);
  setInputLogin(inputLogin);
  storeData('password', inputPassword);
  setInputPassword(inputPassword);
  navigation.navigate('LK');
}
const [inputLogin, setInputLogin] = useState(''); 
const [inputPassword, setInputPassword] = useState(''); 
const [storedLogin, setStoredLogin] = useState('');
const [storedPassword, setStoredPassword] = useState('');


if (storedLogin && storedPassword){
  navigation.navigate('LK');

}

useEffect(() => {
  const fetchData = async () => {
    const login = await getData('login');
    const password = await getData('password');
    if (login) {
      setStoredLogin(login);
    }
    if (password) {
      setStoredPassword(password);
    }
  };

  fetchData();
}, []);



  return (



    
    <View style={styles.container}>
    <Text style={styles.textLast}>Авторизация</Text>
      <TextInput
        style={styles.input}
        onChangeText={setInputLogin}
        value={inputLogin}
        placeholder="Login"
      />
      
      
      <TextInput
        style={styles.input}
        onChangeText={setInputPassword} 
        value={inputPassword}
        placeholder="Password"
      />
      
      <Button style={styles.btn} title={'Продолжить'} onPress={loadscene}/>
      
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
    color:'green', 
    marginBottom: 10
  },
  textLast:
  {
    color:'green', 
    marginTop: 50,
    marginBottom: 10
  },
  
});
