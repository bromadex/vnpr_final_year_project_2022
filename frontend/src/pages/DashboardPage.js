import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useWebSocket } from '../context/WebSocketContext';
import { 
  AlertTriangle, Car, Search, CheckCircle, Clock,
  TrendingUp, MapPin, Activity
} from 'lucide-react';
import { format } from 'date-fns';

const StatCard = ({ title, value, icon: Icon, color, trend }) => (
  <div className="card">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      {trend && (
        <span className="flex items-center text-sm text-green-600">
          <TrendingUp className="w-4 h-4 mr-1" />
          {trend}
        </span>
      )}
    </div>
    <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
    <p className="text-sm text-gray-500">{title}</p>
  </div>
);

const RecentIncident = ({ incident }) => (
  <div className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors">
    <div className="flex items-center gap-4">
      <div className={`p-2 rounded-lg ${
        incident.event_type === 'OVER_SPEEDING' ? 'bg-red-100' : 'bg-orange-100'
      }`}>
        <AlertTriangle className={`w-5 h-5 ${
          incident.event_type === 'OVER_SPEEDING' ? 'text-red-600' : 'text-orange-600'
        }`} />
      </div>
      <div>
        <p className="font-semibold text-gray-900">{incident.number_plate}</p>
        <p className="text-sm text-gray-500">
          {incident.event_type === 'OVER_SPEEDING' ? 'Over Speeding' : 'Red Light'} 
          {' • '}
          {incident.location || 'Location unknown'}
        </p>
      </div>
    </div>
    <span className="text-sm text-gray-400">
      {format(new Date(incident.created_at), 'HH:mm')}
    </span>
  </div>
);

const DashboardPage = () => {
  const [stats, setStats] = useState({
    totalIncidents: 0,
    todayIncidents: 0,
    resolvedIncidents: 0,
    totalVehicles: 0,
  });
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const { lastMessage } = useWebSocket();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Real-time updates
  useEffect(() => {
    if (lastMessage?.type === 'new_incident') {
      setRecentIncidents(prev => [lastMessage.data, ...prev].slice(0, 10));
      setStats(prev => ({
        ...prev,
        totalIncidents: prev.totalIncidents + 1,
        todayIncidents: prev.todayIncidents + 1,
      }));
    }
  }, [lastMessage]);

  const fetchDashboardData = async () => {
    try {
      const [incidentsRes, vehiclesRes] = await Promise.all([
        axios.get('/api/events/list/?page_size=10'),
        axios.get('/api/vehicles/'),
      ]);

      const incidents = incidentsRes.data.results || [];
      const vehicles = vehiclesRes.data.results || [];

      const today = new Date().toISOString().split('T')[0];
      const todayIncidents = incidents.filter(i => 
        i.created_at?.startsWith(today)
      ).length;

      setStats({
        totalIncidents: incidentsRes.data.count || 0,
        todayIncidents,
        resolvedIncidents: incidents.filter(i => i.is_resolved).length,
        totalVehicles: vehiclesRes.data.count || 0,
      });

      setRecentIncidents(incidents.slice(0, 10));
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Overview of traffic violation activity</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Incidents"
          value={stats.totalIncidents}
          icon={AlertTriangle}
          color="bg-red-500"
          trend="+12%"
        />
        <StatCard
          title="Today's Incidents"
          value={stats.todayIncidents}
          icon={Activity}
          color="bg-orange-500"
        />
        <StatCard
          title="Resolved"
          value={stats.resolvedIncidents}
          icon={CheckCircle}
          color="bg-green-500"
          trend="+8%"
        />
        <StatCard
          title="Registered Vehicles"
          value={stats.totalVehicles}
          icon={Car}
          color="bg-blue-500"
        />
      </div>

      {/* Recent Incidents */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Recent Incidents</h2>
          <Link to="/incidents" className="text-primary-500 hover:text-primary-600 text-sm font-medium">
            View All
          </Link>
        </div>

        <div className="space-y-2">
          {recentIncidents.length > 0 ? (
            recentIncidents.map(incident => (
              <RecentIncident key={incident.id} incident={incident} />
            ))
          ) : (
            <p className="text-gray-400 text-center py-8">No incidents recorded yet</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/search" className="card hover:shadow-md transition-shadow group">
          <Search className="w-8 h-8 text-primary-500 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900">Search Vehicle</h3>
          <p className="text-sm text-gray-500 mt-1">Look up vehicle by plate number</p>
        </Link>
        <Link to="/vehicles/add" className="card hover:shadow-md transition-shadow group">
          <Car className="w-8 h-8 text-green-500 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900">Add Vehicle</h3>
          <p className="text-sm text-gray-500 mt-1">Register new vehicle to database</p>
        </Link>
        <Link to="/incidents" className="card hover:shadow-md transition-shadow group">
          <MapPin className="w-8 h-8 text-orange-500 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900">View Map</h3>
          <p className="text-sm text-gray-500 mt-1">See incidents on interactive map</p>
        </Link>
      </div>
    </div>
  );
};

export default DashboardPage;
