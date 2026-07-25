import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Car, ChevronLeft, ChevronRight, Search, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

const VehicleCard = ({ vehicle }) => (
  <Link to={`/vehicles/${vehicle.id}`} className="card hover:shadow-md transition-shadow group">
    <div className="flex items-start gap-4">
      {vehicle.first_image ? (
        <img 
          src={vehicle.first_image} 
          alt={vehicle.vehicle_name}
          className="w-24 h-24 object-cover rounded-lg"
        />
      ) : (
        <div className="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center">
          <Car className="w-8 h-8 text-gray-400" />
        </div>
      )}

      <div className="flex-1">
        <h3 className="font-bold text-lg text-gray-900 group-hover:text-primary-500 transition-colors">
          {vehicle.number_plate}
        </h3>
        <p className="text-gray-600">{vehicle.vehicle_name}</p>
        <p className="text-sm text-gray-500">{vehicle.vehicle_model} • {vehicle.vehicle_owner}</p>
      </div>
    </div>
  </Link>
);

const VehiclesPage = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ next: null, previous: null });

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async (url = '/api/vehicles/') => {
    try {
      setLoading(true);
      const response = await axios.get(url);
      setVehicles(response.data.results || []);
      setPagination({
        next: response.data.next,
        previous: response.data.previous,
      });
    } catch (error) {
      console.error('Failed to fetch vehicles:', error);
      toast.error('Failed to load vehicles');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vehicles</h1>
          <p className="text-gray-500">Registered vehicle database</p>
        </div>
        <Link
          to="/vehicles/add"
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg
                     hover:bg-primary-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Vehicle
        </Link>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {vehicles.map(vehicle => (
              <VehicleCard key={vehicle.id} vehicle={vehicle} />
            ))}
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={() => pagination.previous && fetchVehicles(pagination.previous)}
              disabled={!pagination.previous}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg disabled:opacity-50"
            >
              <ChevronLeft className="w-4 h-4" /> Previous
            </button>
            <button
              onClick={() => pagination.next && fetchVehicles(pagination.next)}
              disabled={!pagination.next}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg disabled:opacity-50"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default VehiclesPage;
