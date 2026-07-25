import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useWebSocket } from '../context/WebSocketContext';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import { 
  AlertTriangle, Filter, CheckCircle, Clock, MapPin,
  ChevronLeft, ChevronRight, Search
} from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

// Custom marker icon
const violationIcon = new Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const IncidentCard = ({ incident, onResolve }) => (
  <div className={`card mb-4 ${incident.is_resolved ? 'opacity-60' : ''}`}>
    <div className="flex items-start justify-between">
      <div className="flex items-start gap-4">
        {incident.image_link ? (
          <img 
            src={incident.image_link} 
            alt="Violation" 
            className="w-32 h-24 object-cover rounded-lg"
          />
        ) : (
          <div className="w-32 h-24 bg-gray-200 rounded-lg flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-gray-400" />
          </div>
        )}

        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-bold text-lg text-gray-900">{incident.number_plate}</h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              incident.event_type === 'OVER_SPEEDING' 
                ? 'bg-red-100 text-red-700' 
                : 'bg-orange-100 text-orange-700'
            }`}>
              {incident.event_type === 'OVER_SPEEDING' ? 'Over Speeding' : 'Red Light'}
            </span>
            {incident.is_resolved && (
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                Resolved
              </span>
            )}
          </div>

          <p className="text-sm text-gray-500 mb-2">{incident.description}</p>

          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {format(new Date(incident.created_at), 'MMM dd, yyyy HH:mm')}
            </span>
            {incident.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                {incident.location}
              </span>
            )}
            {incident.speed && (
              <span className="text-red-500 font-medium">
                {incident.speed.toFixed(1)} km/h
              </span>
            )}
          </div>
        </div>
      </div>

      {!incident.is_resolved && (
        <button
          onClick={() => onResolve(incident.id)}
          className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg
                     hover:bg-green-600 transition-colors text-sm"
        >
          <CheckCircle className="w-4 h-4" />
          Resolve
        </button>
      )}
    </div>
  </div>
);

const IncidentsPage = () => {
  const [incidents, setIncidents] = useState([]);
  const [filter, setFilter] = useState('all');
  const [view, setView] = useState('list'); // 'list' or 'map'
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ next: null, previous: null, count: 0 });
  const { lastMessage } = useWebSocket();

  useEffect(() => {
    fetchIncidents();
  }, [filter]);

  // Real-time updates
  useEffect(() => {
    if (lastMessage?.type === 'new_incident') {
      toast.success(`New violation: ${lastMessage.data.number_plate}`, {
        icon: '🚨',
      });
      fetchIncidents();
    }
  }, [lastMessage]);

  const fetchIncidents = async (url = '/api/events/list/') => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filter !== 'all') {
        params.append('type', filter.toUpperCase());
      }

      const response = await axios.get(`${url}?${params.toString()}`);
      setIncidents(response.data.results || []);
      setPagination({
        next: response.data.next,
        previous: response.data.previous,
        count: response.data.count,
      });
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
      toast.error('Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (id) => {
    try {
      await axios.post(`/api/events/list/${id}/resolve/`);
      toast.success('Incident resolved');
      fetchIncidents();
    } catch (error) {
      toast.error('Failed to resolve incident');
    }
  };

  const filteredIncidents = incidents.filter(i => {
    if (filter === 'all') return true;
    if (filter === 'speeding') return i.event_type === 'OVER_SPEEDING';
    if (filter === 'redlight') return i.event_type === 'RED_ROBOT';
    if (filter === 'unresolved') return !i.is_resolved;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Incidents</h1>
          <p className="text-gray-500">{pagination.count} total violations recorded</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setView('list')}
            className={`px-4 py-2 rounded-lg ${view === 'list' ? 'bg-primary-500 text-white' : 'bg-gray-100'}`}
          >
            List
          </button>
          <button
            onClick={() => setView('map')}
            className={`px-4 py-2 rounded-lg ${view === 'map' ? 'bg-primary-500 text-white' : 'bg-gray-100'}`}
          >
            Map
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        {['all', 'speeding', 'redlight', 'unresolved'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === f 
                ? 'bg-primary-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f === 'all' && 'All Incidents'}
            {f === 'speeding' && 'Over Speeding'}
            {f === 'redlight' && 'Red Light'}
            {f === 'unresolved' && 'Unresolved'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : view === 'list' ? (
        <div>
          {filteredIncidents.length > 0 ? (
            filteredIncidents.map(incident => (
              <IncidentCard 
                key={incident.id} 
                incident={incident} 
                onResolve={handleResolve}
              />
            ))
          ) : (
            <div className="text-center py-16">
              <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No incidents found</p>
            </div>
          )}

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={() => pagination.previous && fetchIncidents(pagination.previous)}
              disabled={!pagination.previous}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg disabled:opacity-50"
            >
              <ChevronLeft className="w-4 h-4" /> Previous
            </button>
            <button
              onClick={() => pagination.next && fetchIncidents(pagination.next)}
              disabled={!pagination.next}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg disabled:opacity-50"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        <div className="h-[600px] rounded-xl overflow-hidden border border-gray-200">
          <MapContainer
            center={[-20.1457, 28.5873]} // Default: Bulawayo, Zimbabwe
            zoom={13}
            className="h-full w-full"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            {filteredIncidents
              .filter(i => i.latitude && i.longitude)
              .map(incident => (
                <Marker
                  key={incident.id}
                  position={[parseFloat(incident.latitude), parseFloat(incident.longitude)]}
                  icon={violationIcon}
                >
                  <Popup>
                    <div className="p-2">
                      <p className="font-bold">{incident.number_plate}</p>
                      <p className="text-sm text-gray-500">
                        {incident.event_type === 'OVER_SPEEDING' ? 'Over Speeding' : 'Red Light'}
                      </p>
                      <p className="text-xs text-gray-400">
                        {format(new Date(incident.created_at), 'MMM dd, HH:mm')}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              ))}
          </MapContainer>
        </div>
      )}
    </div>
  );
};

export default IncidentsPage;
