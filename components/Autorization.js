import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button,TextInput} from 'react-native';

import { Request } from './Requests';
import getData from './getData';
import storeData from './storeData';




export default function Autorization({navigation}) {

const loadscene=()=>{
  storeData('username', inputLogin);
  setInputLogin(inputLogin);
  storeData('password', inputPassword);
  setInputPassword(inputPassword);

  const authorize = Request('POST', 'http://62.109.17.249:8000/react/login', {username: inputLogin, password: inputPassword}).then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error('Error:', error);
  });

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
    const login = await getData('username');
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
