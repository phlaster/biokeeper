import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, Image } from 'react-native';


export default function Ask_autorization({navigation}) {
const loadscene_autorization=()=>{
  navigation.navigate('Autorization');
}
const loadscene_no_autorization=()=>{
  navigation.navigate('Qr_screen');
}

  return (
    <View style={styles.container}>
      
      
      
      <Text style={styles.text}>Продолжить с авторизацией</Text>
       <Button style={styles.btn} title={'Продолжить'} onPress={loadscene_autorization}/>

       <Text style={styles.textLast}>Продолжить без авторизации</Text>
       <Button style={styles.btn} title={'Продолжить'} onPress={loadscene_no_autorization}/>
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
