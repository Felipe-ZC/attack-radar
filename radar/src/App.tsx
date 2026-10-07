import Globe from 'react-globe.gl';
import './App.css';
import { useQuery } from '@tanstack/react-query';

// Same-origin `/api` by default: proxied by Vite in dev and nginx in prod.
const API_URL = import.meta.env.VITE_API_URL || '/api';

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
      const res = await fetch(`${API_URL}/host-metadata?${params}`);
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
        globeImageUrl="/earth-night.jpg"
        pointsData={pointsData} 
      />
      <p className='attribution'>
        Earth texture:{' '}
        <a href='https://www.solarsystemscope.com/textures/' target='_blank' rel='noreferrer'>
          Solar System Scope
        </a>{' '}
        (<a href='https://creativecommons.org/licenses/by/4.0/' target='_blank' rel='noreferrer'>CC BY 4.0</a>)
      </p>
    </div>
  )
}

export default App
