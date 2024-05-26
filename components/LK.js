import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button,TextInput,Image} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Request from './Requests';

export default function LK({navigation}) {
const loadscene=()=>{
  navigation.navigate('Qr_screen');
}
const exit = async()  => {
  login='login';
  password='password';
  try {
    await AsyncStorage.removeItem(login);
    await AsyncStorage.removeItem(password);
    navigation.navigate('Autorization');
  } catch(e) {
    // ошибка при удалении данных
    console.error("Ошибка при удалении данных", e);
  }

};

  return (
    
    <View style={styles.container}>
    
      <Button style={styles.btn} title={'выбрать ресерч'} onPress={loadscene}/>

      <Button style={styles.btn} title={'выйти'} onPress={exit}/>
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
  btn:{
    position:'relative',
    bottom:0
  }
});
