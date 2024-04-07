import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View,Button,Image } from 'react-native';

export default function Bio_info({route}) {
    const loadscene = () => {
        
      };
    const {data} = route.params;
      return (
        <View style={styles.container}>
          
          
          <Text style={styles.text}>{data}</Text>
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
    





