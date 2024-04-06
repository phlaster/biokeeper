import React from "react";
import Qr_screen from  './components/Qr_screen';
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
                name="Qr_screen"
                component={Qr_screen}
                options={{title:'Qr_screen'}}
                />
        
        </Stack.Navigator>
    </NavigationContainer>;
}
