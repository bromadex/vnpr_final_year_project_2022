import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import { ArrowLeft, AlertTriangle, Clock, MapPin, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

const IncidentDetailPage = () => {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const fetchIncident = async () => {
    try {
      const response = await axios.get(`/api/events/list/${id}/`);
      setIncident(response.data);
    } catch (error) {
      toast.error('Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    try {
      await axios.post(`/api/events/list/${id}/resolve/`);
      toast.success('Incident resolved');
      fetchIncident();
    } catch (error) {
      toast.error('Failed to resolve');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!incident) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/incidents" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Incident Details</h1>
        </div>
        {!incident.is_resolved && (
          <button
            onClick={handleResolve}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            <CheckCircle className="w-4 h-4" />
            Mark Resolved
          </button>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          {incident.image_link ? (
            <img 
              src={incident.image_link} 
              alt="Violation"
              className="w-full h-64 object-cover rounded-lg mb-4"
            />
          ) : (
            <div className="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center mb-4">
              <AlertTriangle className="w-16 h-16 text-gray-400" />
            </div>
          )}

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h2 className="text-2xl font-bold text-gray-900">{incident.number_plate}</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                incident.event_type === 'OVER_SPEEDING' 
                  ? 'bg-red-100 text-red-700' 
                  : 'bg-orange-100 text-orange-700'
              }`}>
                {incident.event_type === 'OVER_SPEEDING' ? 'Over Speeding' : 'Red Light'}
              </span>
            </div>

            <p className="text-gray-600">{incident.description}</p>

            <div className="space-y-2 pt-4">
              <div className="flex items-center gap-2 text-gray-500">
                <Clock className="w-4 h-4" />
                <span>{format(new Date(incident.created_at), 'PPP p')}</span>
              </div>
              {incident.location && (
                <div className="flex items-center gap-2 text-gray-500">
                  <MapPin className="w-4 h-4" />
                  <span>{incident.location}</span>
                </div>
              )}
              {incident.speed && (
                <div className="text-red-500 font-medium">
                  Speed: {incident.speed.toFixed(1)} km/h
                </div>
              )}
            </div>

            {incident.is_resolved && (
              <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">This incident has been resolved</span>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Location</h3>
          {incident.latitude && incident.longitude ? (
            <div className="h-64 rounded-lg overflow-hidden">
              <MapContainer
                center={[parseFloat(incident.latitude), parseFloat(incident.longitude)]}
                zoom={15}
                className="h-full w-full"
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; OpenStreetMap contributors'
                />
                <Marker position={[parseFloat(incident.latitude), parseFloat(incident.longitude)]} />
              </MapContainer>
            </div>
          ) : (
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-400">No location data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IncidentDetailPage;
