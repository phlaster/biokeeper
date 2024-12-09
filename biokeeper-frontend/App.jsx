import { Provider as PaperProvider } from 'react-native-paper';
import MainStack from './navigate';

const App = () => {
  return (
    <PaperProvider>
      <MainStack />
    </PaperProvider>
  );
};

export default App;