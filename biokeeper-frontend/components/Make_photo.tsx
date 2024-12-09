import React, { useState, useEffect, useRef } from 'react';
import { Dimensions, Alert, Vibration, Button, Pressable, Text, View, Image } from "react-native";
import { Camera, CameraType } from 'expo-camera/legacy';
import * as MediaLibrary from 'expo-media-library';
import { router } from "expo-router";
import * as Linking from "expo-linking";

function Make_photo({ navigation }) {
  const [hasCameraPermission, setCameraPermission] = useState<boolean | null>(null);
  const [hasAudioPermission, setAudioPermission] = useState<boolean | null>(null);
  const [hasMediaLibraryPermission, setMediaLibraryPermission] = useState<boolean | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const cameraRef = useRef<Camera>(null);

  useEffect(() => {
    const requestPermissions = async () => {
      const cameraPermission = await Camera.requestCameraPermissionsAsync();
      const audioPermission = await Camera.requestMicrophonePermissionsAsync();
      const mediaLibraryPermission = await MediaLibrary.requestPermissionsAsync(); 

      setCameraPermission(cameraPermission.status === "granted");
      setAudioPermission(audioPermission.status === "granted");
      setMediaLibraryPermission(mediaLibraryPermission.status === "granted");
    };

    requestPermissions();
  }, []);

  useEffect(() => {
    if (hasCameraPermission !== null && hasAudioPermission !== null) {
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

  const goToSettings = () => {
    Linking.openSettings();
  };

  const __takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync();
      console.log(photo);
      setPreviewVisible(true);
      setCapturedImage(photo);
    }
  };

  const __savePhoto = async () => {
    if (capturedImage && hasMediaLibraryPermission) {
      try {
        await MediaLibrary.saveToLibraryAsync(capturedImage.uri);
        navigation.navigate('Take_photo')
        Alert.alert('Photo saved successfully!');
        setCapturedImage(null);
        setPreviewVisible(false);
      } catch (error) {
        console.log(error);
        Alert.alert('Failed to save photo.');
      }
    }
  };

  const __retakePicture = () => {
    setCapturedImage(null);
    setPreviewVisible(false);
  };

  if (hasCameraPermission && hasAudioPermission) {
    return (
      <View style={{ flex: 1 }}>
        {previewVisible && capturedImage ? (
          <View style={{ flex: 1 }}>
            <Image source={{ uri: capturedImage.uri }} style={{ flex: 1 }} />
            <Button title="Retake" onPress={__retakePicture} />
            <Button title="Save" onPress={__savePhoto} />{}
          </View>
        ) : (
          <>
            <Camera
              ref={cameraRef}
              style={{ flex: 1 }}
              type={CameraType.back} // исправлено
            >
              <View
                style={{
                  flex: 1,
                  backgroundColor: 'transparent',
                  flexDirection: 'row',
                  justifyContent: 'center',
                  alignItems: 'flex-end',
                }}
              >
                <Pressable
                  onPress={__takePicture}
                  style={{
                    width: 70,
                    height: 70,
                    bottom: 30,
                    borderRadius: 35,
                    backgroundColor: '#fff',
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                >
                  <Text style={{ fontSize: 18 }}>Snap</Text>
                </Pressable>
              </View>
            </Camera>
          </>
        )}
      </View>
    );
  }

  return null;
}
export default Make_photo;