import { useState, useEffect } from "react";
import { Dimensions, Alert, Vibration,Button } from "react-native";
import { Camera,CameraView } from 'expo-camera';
import { router } from "expo-router";
import * as Linking from "expo-linking";



function QRScanner({ navigation }) {

  const [hasCameraPermission, setCameraPermission] = useState<boolean | null>(
    null
  );
  const [hasAudioPermission, setAudioPermission] = useState<boolean | null>(
    null
  );

  useEffect(() => {
    const requestPermissions = async () => {
      const cameraPermission = await Camera.requestCameraPermissionsAsync();
      const audioPermission = await Camera.requestMicrophonePermissionsAsync();

      setCameraPermission(cameraPermission.status === "granted");
      setAudioPermission(audioPermission.status === "granted");
    };

    requestPermissions();
  }, []);

  useEffect(() => {
    if (hasCameraPermission !== null && hasAudioPermission !== null) {
      // Check permissions and execute logic when both permissions are set
      if (!hasCameraPermission || !hasAudioPermission) {
        Alert.alert(
          "Camera Permissions Required",
          "You must grant access to your camera to scan QR codes",
          [
            { text: "Go to settings", onPress: goToSettings },
            {
              text: "Cancel",
              onPress: () => {
                router.dismissAll();
              },
              style: "cancel",
            },
          ]
        );
      }
    }
  }, [hasCameraPermission, hasAudioPermission]);

  const handleBarCodeScanned = async ({ data }) => {
    Vibration.vibrate();
    navigation.navigate('Bio_info', { data: data });
  };
  const handleBarCodeScannedTest = async () => {
    
    navigation.navigate('Bio_info', { data: '123'});
  };

  const goToSettings = () => {
    Linking.openSettings();
  };

  
  

  if (hasCameraPermission && hasAudioPermission) {


    return (
      <><Button title="Сохранить" onPress={handleBarCodeScannedTest} />
      <CameraView
        onBarcodeScanned={handleBarCodeScanned}
        barcodeScannerSettings={{
          barcodeTypes: ["qr"],
        }}

        style={{ height: Dimensions.get("window").height }} /></>
    );
  }
}

export default QRScanner;
