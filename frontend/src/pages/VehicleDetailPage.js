import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Car, Edit, Trash2, ArrowLeft, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';

const VehicleDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    fetchVehicle();
  }, [id]);

  const fetchVehicle = async () => {
    try {
      const response = await axios.get(`/api/vehicles/${id}/`);
      setVehicle(response.data);
    } catch (error) {
      toast.error('Failed to load vehicle details');
      navigate('/vehicles');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`/api/vehicles/${id}/delete/`);
      toast.success('Vehicle deleted');
      navigate('/vehicles');
    } catch (error) {
      toast.error('Failed to delete vehicle');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!vehicle) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/vehicles" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Vehicle Details</h1>
      </div>

      <div className="card">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            {vehicle.images && vehicle.images.length > 0 ? (
              <img 
                src={vehicle.images[0].image} 
                alt={vehicle.vehicle_name}
                className="w-full h-64 object-cover rounded-lg"
              />
            ) : (
              <div className="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center">
                <Car className="w-16 h-16 text-gray-400" />
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <h2 className="text-3xl font-bold text-primary-600">{vehicle.number_plate}</h2>
              <p className="text-xl text-gray-600">{vehicle.vehicle_name}</p>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Owner</span>
                <span className="font-medium">{vehicle.vehicle_owner}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Model</span>
                <span className="font-medium">{vehicle.vehicle_model}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Year</span>
                <span className="font-medium">{vehicle.year}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Address</span>
                <span className="font-medium">{vehicle.vehicle_owner_address}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-500">Phone</span>
                <span className="font-medium">{vehicle.vehicle_owner_phone}</span>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
                <Edit className="w-4 h-4" /> Edit
              </button>
              <button 
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                <Trash2 className="w-4 h-4" /> Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-8 h-8 text-red-500" />
              <h3 className="text-lg font-bold">Delete Vehicle?</h3>
            </div>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this vehicle? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VehicleDetailPage;
