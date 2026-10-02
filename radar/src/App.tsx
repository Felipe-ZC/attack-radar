import Globe from 'react-globe.gl';
import './App.css';
import { useQuery } from '@tanstack/react-query';

const getRandomSize = () => Math.random() / 3;
const getRandomColor = () => ['red', 'white', 'blue', 'green'][Math.round(Math.random() * 3)];

/** ISO 8601 datetime string */
type ISODateTime = string;

/** IPv4 or IPv6 address as a string */
type IPAddress = string;

export interface HostMetadata {
  id: number | null;
  ipAddress: IPAddress;
  countryCode: string | null;
  countryName: string | null;
  usageType: string | null;
  domain: string | null;
  isp: string | null;
  /** Range: -90 to 90 (enforced server-side only) */
  lat: number | null;
  /** Range: -180 to 180 (enforced server-side only) */
  lon: number | null;
  createdAt: ISODateTime | null;
  modifiedAt: ISODateTime | null;
}

export interface AbuseReport {
  ipAddress: IPAddress;
  reportTimestamp: ISODateTime;
  reportComment: string | null;
  reportCategories: number[];
  createdAt: ISODateTime | null;
  modifiedAt: ISODateTime | null;
}


function App() {
  const { data: hostMetadata, isPending, error } = useQuery({
    queryKey: ['hostMetadata'],
    queryFn: async (): Promise<HostMetadata[]> => {
      const params = new URLSearchParams({size: '1000'});
      const res = await fetch(`http://localhost:8000/host-metadata?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
  });

  if (error) return <p>Error: {error.message}</p>;
  if (isPending) return <p>Loading…</p>;
  
  const pointsData = hostMetadata.map((host) => ({
    lat: host.lat,
    lng: host.lon,
    size: getRandomSize(),
    color: getRandomColor() 
  }));

  return (
    <div className='App'>
      <Globe 
        globeImageUrl="https://upload.wikimedia.org/wikipedia/commons/2/2f/Solarsystemscope_texture_2k_earth_nightmap.jpg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original"
        pointsData={pointsData} 
      />
    </div>
  )
}

export default App
