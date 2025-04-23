import React, { useState } from 'react';
import { View, Alert } from 'react-native';
import { TextInput, Button, Text, Surface } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import styles from '../styles/style';
import getData from './getData';
import { reg, auth } from './Authfunc';
import storeData from './storeData';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Registration({ navigation }) {
  const [inputLogin, setInputLogin] = useState('');
  const [inputEmail, setInputEmail] = useState('');
  const [inputPassword, setInputPassword] = useState('');
  const [inputPassword2, setInputPassword2] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleRegistration = async () => {
    setLoading(true);
    try {
      await reg({
        username: inputLogin,
        email: inputEmail,
        password: inputPassword,
        password2: inputPassword2
      });

      const authStatus = await getData("authStatus");
      if (authStatus && authStatus.error) {
        Alert.alert("Error", authStatus.error);
      } else {
        await auth({
          grant_type: 'password',
          username: inputLogin,
          password: inputPassword
        });

        await storeData("current_user", inputLogin);
        await storeData("current_password", inputPassword);
        await storeData("last_login", new Date().toISOString());

        navigation.navigate('LK');
      }
    } catch (error) {
      console.error('Error:', error);
      Alert.alert('Error', `An error occurred during registration.\n${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const passwordsMatch = inputPassword === inputPassword2;
  const emailIsValid = EMAIL_REGEX.test(inputEmail);

  const passwordLengthGE = inputPassword.length >= 8;
  const passwordLengthLE = inputPassword.length <= 32;
  const hasLowercase = /[a-z]/.test(inputPassword);
  const hasUppercase = /[A-Z]/.test(inputPassword);
  const hasNumber = /\d/.test(inputPassword);
  const hasSpecialChar = /\W|_/g.test(inputPassword);

  let passwordWeaknessMessage = '';
  if (!passwordLengthGE) {
    passwordWeaknessMessage = 'Too short for a password';
  } else if (!passwordLengthLE) {
    passwordWeaknessMessage = 'Not too long!';
  } else if (!hasLowercase) {
    passwordWeaknessMessage = 'Need lowercase letters';
  } else if (!hasUppercase) {
    passwordWeaknessMessage = 'Need uppercase letters';
  } else if (!hasNumber) {
    passwordWeaknessMessage = 'Need a number';
  } else if (!hasSpecialChar) {
    passwordWeaknessMessage = 'Need a special character';
  }

  let buttonLabel = 'Set your new login';
  if (inputLogin) {
    if (!inputEmail) {
      buttonLabel = 'Enter your email';
    } else if (!emailIsValid) {
      buttonLabel = 'Enter a valid email, please!';
    } else if (!inputPassword) {
      buttonLabel = 'Enter your password';
    } else if (passwordWeaknessMessage) {
      buttonLabel = passwordWeaknessMessage;
    } else if (!passwordsMatch) {
      buttonLabel = 'Passwords don\'t match';
    } else {
      buttonLabel = 'Sign up!';
    }
  }

  const isButtonDisabled = loading || !inputLogin || !inputEmail || !emailIsValid || !inputPassword || passwordWeaknessMessage || !passwordsMatch;

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      <Surface style={styles.authSurface}>
        <Text style={styles.title}>Registration</Text>
        <TextInput
          style={styles.input}
          label="Login"
          mode="outlined"
          value={inputLogin}
          onChangeText={setInputLogin}
        />
        <TextInput
          style={styles.input}
          label="Email"
          mode="outlined"
          value={inputEmail}
          onChangeText={setInputEmail}
          keyboardType="email-address"
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
        <TextInput
          style={styles.input}
          label="Repeat Password"
          mode="outlined"
          value={inputPassword2}
          onChangeText={setInputPassword2}
          secureTextEntry={!showPassword}
          right={<TextInput.Icon />}
          editable={!passwordWeaknessMessage}
        />
        <Button
          mode="contained"
          style={styles.button}
          onPress={handleRegistration}
          loading={loading}
          disabled={isButtonDisabled}
        >
          {buttonLabel}
        </Button>
        <Button
          mode="text"
          onPress={() => navigation.navigate('Authorization')}
          style={styles.textButton}
        >
          Already have an account? Log in
        </Button>
      </Surface>
    </View>
  );
}