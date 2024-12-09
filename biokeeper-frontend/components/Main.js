import { MaterialIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { View, Image } from 'react-native';
import { Button, Text, Surface } from 'react-native-paper';

import {sharedStyles, theme} from '../styles/style';
import { StyleSheet } from 'react-native';

export default function Main({ navigation }) {
  const handleStart = () => {
    navigation.navigate('Authorization');
  };

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      <Surface style={styles.mainSurface}>
        <Image
          style={styles.logo}
          source={require('../assets/Biokeeper.png')}
          resizeMode="contain"
        />
        <Text style={styles.mainTitle}>Biokeeper</Text>
        <Text style={styles.mainText}>
        Citizen science biosample annotation tool 
        </Text>
        <Button
          mode="contained"
          icon={({ color }) => <MaterialIcons name="arrow-forward" size={24} color={color} />}
          onPress={handleStart}
          style={styles.mainButton}
          contentStyle={styles.mainButtonContent}
        >
          Начать
        </Button>
      </Surface>
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mainSurface: {
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  logo: {
    height: 200,
  },
  mainTitle: {
    fontSize: 31,
    fontWeight: 'bold',
    marginVertical: 10,
  },
  mainText: {
    textAlign: 'center',
    marginBottom: 20,
  },
  mainButton: {
    marginTop: 20,
  },
  mainButtonContent: {
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
});