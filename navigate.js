import React from "react";
import Qr_screen from  './components/Qr_screen';
import Main from  './components/Main';
import Bio_info from  './components/Bio_info';
import Take_photo from './components/Take_photo';
import Autorization from './components/Autorization';
import ResearchComment from './components/ResearchComment';
import LK from './components/LK';
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
                name="Autorization"
                component={Autorization}
                options={{title:'Autorization'}}
                /> 
            <Stack.Screen
                name="LK"
                component={LK}
                options={{title:'LK'}}
                />   
            <Stack.Screen
                name="ResearchComment"
                component={ResearchComment}
                options={{title:'ResearchComment'}}
                />
            <Stack.Screen
                name="Qr_screen"
                component={Qr_screen}
                options={{title:'Qr_screen'}}
                />
            <Stack.Screen
                name="Bio_info"
                component={Bio_info}
                options={{title:'Bio_info'}}
                />
            <Stack.Screen
                name="Take_photo"
                component={Take_photo}
                options={{title:'Take_photo'}}
                />
        
        </Stack.Navigator>
    </NavigationContainer>;
}
