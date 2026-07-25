import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, ArrowRight, Camera, MapPin, Zap } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700">
      <div className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Shield className="w-20 h-20 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-white mb-4">
            VNPR System
          </h1>
          <p className="text-xl text-primary-100 max-w-2xl mx-auto">
            Intelligent Traffic Violation Detection using AI-Powered License Plate Recognition
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 text-white">
            <Camera className="w-10 h-10 mb-4" />
            <h3 className="text-xl font-semibold mb-2">AI Recognition</h3>
            <p className="text-primary-100">
              Google Cloud Vision powered OCR with 95%+ accuracy for license plates
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 text-white">
            <Zap className="w-10 h-10 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Real-Time Alerts</h3>
            <p className="text-primary-100">
              Instant violation notifications via WebSocket to enforcement officers
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 text-white">
            <MapPin className="w-10 h-10 mb-4" />
            <h3 className="text-xl font-semibold mb-2">GPS Tracking</h3>
            <p className="text-primary-100">
              Precise location mapping of every violation with interactive maps
            </p>
          </div>
        </div>

        <div className="text-center">
          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-600 
                       rounded-xl font-semibold hover:bg-gray-100 transition-colors"
          >
            Access Dashboard
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
