import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, Image } from 'react-native';


export default function Main({navigation}) {
const loadscene=()=>{
  navigation.navigate('Autorization');
}

  return (
    <View style={styles.container}>
      
      
      <Image 
      style={styles.logo}
      source={require('../assets/Biokepper.png')}/>
      <Text style={styles.text}>Здравствуйте, это приложение для сбора метаданных биологических образцов, проект студентов политеха</Text>
       <Button title={'Начать'} onPress={loadscene}/>
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
    color:'green'
  },
  logo: {
    width: 250,
    height: 250,
  },
});
