import { createStackNavigator } from "@react-navigation/stack";
import { NavigationContainer } from "@react-navigation/native";

import Qr_screen from './components/Qr_screen';
import Main from './components/Main';
import After_Scan from './components/After_Scan';
import Take_photo from './components/Take_photo';
import Authorization from './components/Authorization';
import ResearchComment from './components/ResearchComment';
import Make_photo from "./components/Make_photo";
import Registration from "./components/Registarion";
import LK from './components/LK';
import MyScans from "./components/MyScans";

const Stack = createStackNavigator();
export default function Navigate() {
    return <NavigationContainer>
        <Stack.Navigator>
            <Stack.Screen
                name="Main"
                component={Main}
                options={{ title: 'Main' }}
            />
            <Stack.Screen
                name="Authorization"
                component={Authorization}
                options={{ title: 'Authorization' }}
            />
            <Stack.Screen
                name="LK"
                component={LK}
                options={{ title: 'LK' }}
            />
            <Stack.Screen
                name="ResearchComment"
                component={ResearchComment}
                options={{ title: 'ResearchComment' }}
            />
            <Stack.Screen
                name="Qr_screen"
                component={Qr_screen}
                options={{ title: 'Qr_screen' }}
            />
            <Stack.Screen
                name="After_Scan"
                component={After_Scan}
                options={{ title: 'After_Scan' }}
            />
            <Stack.Screen
                name="Take_photo"
                component={Take_photo}
                options={{ title: 'Take_photo' }}
            />
            <Stack.Screen
                name="Make_photo"
                component={Make_photo}
                options={{ title: 'Make_photo' }}
            />
            <Stack.Screen
                name="Registration"
                component={Registration}
                options={{ title: 'Registration' }}
            />
            <Stack.Screen
                name="MyScans"
                component={MyScans}
                options={{ title: 'MyScans' }}
            />

        </Stack.Navigator>
    </NavigationContainer>;
}
