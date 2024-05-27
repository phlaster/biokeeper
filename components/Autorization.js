import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, TextInput, Alert } from 'react-native';

import getData from './getData';
import storeData from './storeData';

const Request = async (method, url, data) => {
    try {
      const response = await fetch(url + "?" + new URLSearchParams(data).toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
  
      const resp = await response.json();
  
      return resp;
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
      throw error;
    }
  }

export default function Authorization({ navigation }) {
  const [inputLogin, setInputLogin] = useState('');
  const [inputPassword, setInputPassword] = useState('');
  const [storedLogin, setStoredLogin] = useState('');
  const [storedPassword, setStoredPassword] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      const login = await getData('username');
      const password = await getData('password');
      if (login && password) {
        setStoredLogin(login);
        setStoredPassword(password);
        navigation.navigate('LK');
      }
    };

    fetchData();
  }, []);

  const loadScene = async () => {
    try {
      const data = await Request('POST', 'http://62.109.17.249:8000/react/login', {
        username: inputLogin,
        password: inputPassword
      });
      console.log(data);

      if (data.result) {
        await storeData('username', inputLogin);
        await storeData('password', inputPassword);
        navigation.navigate('LK');
      } else {
        Alert.alert(data.response);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

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
        secureTextEntry={true}  // Скрытие пароля
      />
      <Button style={styles.btn} title={'Продолжить'} onPress={loadScene} />
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
    },
  textLast: {
    color: 'green',
    marginTop: 50,
    marginBottom: 10,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 12,
    paddingLeft: 8,
    width: '80%',
  },
});
