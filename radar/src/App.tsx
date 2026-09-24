import Globe from 'react-globe.gl';
import './App.css';

const getRandomLat = () => (Math.random() - 0.5) * 180;
const getRandomLng = () => (Math.random() - 0.5) * 360;
const getRandomSize = () => Math.random() / 3;
const getRandomColor = () => ['red', 'white', 'blue', 'green'][Math.round(Math.random() * 3)];

function App() {
  const N = 300;
  const myData = [...Array(N).keys()].map(() => ({
    lat: getRandomLat(),
    lng: getRandomLng(),
    size: getRandomSize(),
    color: getRandomColor() 
  }));
  return (<Globe pointsData={myData} />);
}

export default App
