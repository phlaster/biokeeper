import React, { useState, useEffect } from 'react';
import { View, Alert } from 'react-native';
import { TextInput, Button, Text, Surface } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';

import { StyleSheet } from 'react-native';

import getData from './getData';
import { auth } from './Authfunc';
import storeData from './storeData';

export default function Authorization({ navigation }) {
  const [inputLogin, setInputLogin] = useState('');
  const [inputPassword, setInputPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await getData('access_token');
      if (token) {
        navigation.navigate('LK');
      }
    } catch (error) {
      console.error('Error checking auth:', error);
      Alert.alert('Error', `Error checking auth\n${error}`, [{ text: 'OK' }]);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    try {
      const authStatus = await auth({
        grant_type: 'password',
        username: inputLogin,
        password: inputPassword,
      });
      if (authStatus === 401) {
        Alert.alert('Error', 'Incorrect login or password!', [{ text: 'OK' }]);
      } else {
        await storeData("login", inputLogin);
        await storeData("current_user", inputLogin);
        await storeData("current_password", inputPassword);
        await storeData("last_login", new Date().toISOString());
        navigation.navigate('LK');
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        Alert.alert('Error', 'Incorrect login or password!', [{ text: 'OK' }]);
      } else {
        console.error('Network error:', error);
        try {
          const storedUser = await getData('current_user');
          const storedPassword = await getData('current_password');
          if (storedUser === inputLogin && storedPassword === inputPassword) {
            await storeData("offline_mode", '1');
            Alert.alert('Going offline', 'Network is unavailable, but you can continue offline.', [
              { text: 'OK', onPress: () => navigation.navigate('LK') }
            ]);
          } else {
            Alert.alert('Offline login failed', 'Network is unavailable, offline login failed.', [{ text: 'OK' }]);
          }
        } catch (storageError) {
          console.error('Storage error:', storageError);
          Alert.alert('Error', 'An error occurred while checking offline login.', [{ text: 'OK' }]);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      <Surface style={styles.authSurface}>
        <Text style={styles.title}>Welcome Back</Text>
        <TextInput
          style={styles.input}
          label="Login"
          mode="outlined"
          value={inputLogin}
          onChangeText={setInputLogin}
        />
        <TextInput
          style={styles.input}
          label="Password"
          mode="outlined"
          value={inputPassword}
          onChangeText={setInputPassword}
          secureTextEntry={!showPassword}
          right={<TextInput.Icon icon={showPassword ? "eye-off" : "eye"} onPress={() => setShowPassword(!showPassword)} />}
        />
        <Button
          mode="contained"
          style={styles.button}
          loading={loading}
          onPress={handleLogin}
          disabled={loading || !inputLogin || !inputPassword}
        >
          {loading ? 'Logging in...' : 'Log in'}
        </Button>
        <Button
          mode="text"
          onPress={() => navigation.navigate('Registration')}
          style={styles.textButton}
        >
          Don't have an account? Sign up
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
  authSurface: {
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  input: {
    width: '100%',
    marginBottom: 10,
  },
  button: {
    marginTop: 20,
  },
  textButton: {
    marginTop: 10,
  },
});