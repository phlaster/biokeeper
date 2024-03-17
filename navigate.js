import React from "react";
import qr_screen from  './components/qr_screen';
import Main from  './components/Main';
import { createStackNavigator } from "@react-navigation/stack";
import { NavigationContainer } from "@react-navigation/native";


const Stack=createStackNavigator();
export default function Navigate(){
    return <NavigationContainer>
        <Stack.Navigator>
            <Stack.Screen
                name="Main"
                component={Main}
                options={{title:'Main'}}
                />
            <Stack.Screen
                name="qr_screen"
                component={qr_screen}
                options={{title:'qr_screen'}}
                />
        
        </Stack.Navigator>
    </NavigationContainer>;
}
