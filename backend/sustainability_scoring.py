from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass

from dataprocessing import (
    LogisticsSustainabilityPipeline
)

@dataclass
class SustainabilityMetrics:
    psi: float  # Package Sustainability Index
    res: float  # Route Efficiency Score
    cei: float  # Carbon Emission Index
    rur: float  # Resource Utilization Rate
    eer: float  # Energy Efficiency Rating
    wrs: float  # Waste Reduction Score

class SustainabilityScoring:
    def __init__(self):
        self.weights = {
            'psi': 0.2,
            'res': 0.2,
            'cei': 0.2,
            'rur': 0.15,
            'eer': 0.15,
            'wrs': 0.1
        }
        
    def calculate_psi(self, package_data: List[Dict]) -> float:
        """Calculate Package Sustainability Index"""
        scores = []
        for package in package_data:
            material_scores = {
                'cardboard': 0.9,
                'paper': 0.85,
                'plastic': 0.4,
                'metal': 0.7,
                'glass': 0.8,
                'wood': 0.75
            }
            material_score = material_scores.get(package['material_type'].lower(), 0.3)
            
            dimensions = package['dimensions']
            volume = dimensions['length'] * dimensions['width'] * dimensions['height']
            density = package['weight'] / volume if volume > 0 else 0
            volume_score = min(density / 0.1, 1.0)  # Normalize density score
            recyclable_bonus = 1.2 if package.get('recyclable', False) else 1.0
            
            package_score = (material_score * 0.4 + volume_score * 0.6) * recyclable_bonus
            scores.append(package_score)
            
        return np.mean(scores) * 100 if scores else 0

    def calculate_res(self, origin: Dict[str, float], destination: Dict[str, float], 
                     transport_mode: str, distance: float) -> float:
        """Calculate Route Efficiency Score"""
        mode_factors = {
            'truck': 0.7,
            'train': 0.9,
            'ship': 0.85,
            'air': 0.3
        }
        
        optimal_distance = distance
        
        actual_distance = distance  # TODO, get from routing API
        directness_score = min(optimal_distance / actual_distance, 1.0) if actual_distance > 0 else 0
        
        mode_score = mode_factors.get(transport_mode.lower(), 0.5)
        
        return (directness_score * 0.6 + mode_score * 0.4) * 100

    def calculate_cei(self, distance: float, transport_mode: str, 
                     total_weight: float) -> float:
        """Calculate Carbon Emission Index"""
        #  (kg CO2 per tonne-km)
        emission_factors = {
            'truck': 0.062,
            'train': 0.022,
            'ship': 0.015,
            'air': 0.602
        }
        
        factor = emission_factors.get(transport_mode.lower(), 0.062)
        emissions = (distance * total_weight / 1000) * factor
        
        # Score inversely proportional to emissions (normalized)
        max_emissions = (distance * total_weight / 1000) * max(emission_factors.values())
        score = (1 - (emissions / max_emissions)) * 100
        
        return max(0, min(score, 100))

    def calculate_rur(self, packages: List[Dict], container_capacity: Dict) -> float:
        """Calculate Resource Utilization Rate"""
        total_volume = sum(
            p['dimensions']['length'] * p['dimensions']['width'] * p['dimensions']['height']
            for p in packages
        )
        total_weight = sum(p['weight'] for p in packages)
        
        volume_utilization = min(total_volume / container_capacity['volume'], 1.0)
        weight_utilization = min(total_weight / container_capacity['max_weight'], 1.0)
        
        return (volume_utilization * 0.5 + weight_utilization * 0.5) * 100

    def calculate_eer(self, transport_mode: str, distance: float, 
                     total_weight: float) -> float:
        """Calculate Energy Efficiency Rating"""
        # Energy consumption factors (MJ/tonne-km)
        energy_factors = {
            'truck': 2.5,
            'train': 0.6,
            'ship': 0.2,
            'air': 8.0
        }
        
        factor = energy_factors.get(transport_mode.lower(), 2.5)
        energy_consumption = (distance * total_weight / 1000) * factor
        
        # Score inversely proportional to energy consumption (normalized)
        max_consumption = (distance * total_weight / 1000) * max(energy_factors.values())
        score = (1 - (energy_consumption / max_consumption)) * 100
        
        return max(0, min(score, 100))

    def calculate_wrs(self, packages: List[Dict]) -> float:
        """Calculate Waste Reduction Score"""
        scores = []
        for package in packages:
            recyclable_score = 100 if package.get('recyclable', False) else 40
            
            material_efficiency = {
                'cardboard': 90,
                'paper': 85,
                'plastic': 40,
                'metal': 80,
                'glass': 75,
                'wood': 70
            }
            material_score = material_efficiency.get(package['material_type'].lower(), 30)
            
            dimensions = package['dimensions']
            volume = dimensions['length'] * dimensions['width'] * dimensions['height']
            density = package['weight'] / volume if volume > 0 else 0
            optimization_score = min(density / 0.1, 1.0) * 100
            
            package_score = (recyclable_score * 0.4 + material_score * 0.3 + 
                           optimization_score * 0.3)
            scores.append(package_score)
            
        return np.mean(scores) if scores else 0

    def calculate_overall_score(self, metrics: SustainabilityMetrics) -> float:
        """Calculate overall sustainability score"""
        scores = {
            'psi': metrics.psi,
            'res': metrics.res,
            'cei': metrics.cei,
            'rur': metrics.rur,
            'eer': metrics.eer,
            'wrs': metrics.wrs
        }
        
        weighted_score = sum(score * self.weights[metric] 
                           for metric, score in scores.items())
        
        return round(weighted_score, 2)

class SustainabilityPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_columns = [
            'distance', 'weight', 'volume', 'is_recyclable', 
            'transport_mode_encoded', 'material_type_encoded'
        ]
        self.is_fitted = False
        
    def prepare_features(self, data: Dict) -> pd.DataFrame:
        """Prepare features for ML model"""
        features = {
            'distance': self._calculate_distance(data['origin'], data['destination']),
            'weight': sum(p['weight'] for p in data['packages']),
            'volume': sum(
                p['dimensions']['length'] * p['dimensions']['width'] * p['dimensions']['height']
                for p in data['packages']
            ),
            'is_recyclable': all(p.get('recyclable', False) for p in data['packages']),
            'transport_mode_encoded': self._encode_transport_mode(data['transport_mode']),
            'material_type_encoded': self._encode_material_type(
                data['packages'][0]['material_type']
            )
        }
        return pd.DataFrame([features])

    def train(self, historical_data: List[Dict], historical_scores: List[float]):
        """Train the ML model on historical data"""
        X = pd.DataFrame([self.prepare_features(data).iloc[0] 
                         for data in historical_data])
        y = np.array(historical_scores)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_fitted = True
        
        # model performance metrics
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        return {
            'train_score': train_score,
            'test_score': test_score
        }

    def predict_sustainability(self, shipment_data: Dict) -> Dict[str, float]:
        """Predict sustainability metrics for new shipment"""
        if not self.is_fitted:
            raise ValueError("Model needs to be trained before making predictions. Call train() first.")
            
        features = self.prepare_features(shipment_data)
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        
        importances = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        return {
            'predicted_score': prediction,
            'feature_importances': importances
        }
    def _encode_transport_mode(self, mode: str) -> int:
        """Encode transport mode as integer"""
        modes = {'truck': 0, 'train': 1, 'ship': 2, 'air': 3}
        return modes.get(mode.lower(), 0)

    def _encode_material_type(self, material: str) -> int:
        """Encode material type as integer"""
        materials = {
            'cardboard': 0, 'paper': 1, 'plastic': 2,
            'metal': 3, 'glass': 4, 'wood': 5
        }
        return materials.get(material.lower(), 0)

    def _calculate_distance(self, origin: Dict[str, float], 
                          destination: Dict[str, float]) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = origin['lat'], origin['long']
        lat2, lon2 = destination['lat'], destination['long']
        
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)

        a = np.sin(delta_phi/2)**2 + \
            np.cos(phi1) * np.cos(phi2) * \
            np.sin(delta_lambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c

# Example usage:
def analyze_sustainability(pipeline: LogisticsSustainabilityPipeline,
                              shipment_data: Dict,
                              predictor: SustainabilityPredictor = None) -> Dict:
    scorer = SustainabilityScoring()
    
    if predictor is None:
        predictor = SustainabilityPredictor()
    
    processed_data = pipeline.process_data(shipment_data)
    
    metrics = SustainabilityMetrics(
        psi=scorer.calculate_psi(shipment_data['packages']),
        res=scorer.calculate_res(
            shipment_data['origin'],
            shipment_data['destination'],
            shipment_data['transport_mode'],
            pipeline._calculate_distance(
                shipment_data['origin'],
                shipment_data['destination']
            )
        ),
        cei=scorer.calculate_cei(
            pipeline._calculate_distance(
                shipment_data['origin'],
                shipment_data['destination']
            ),
            shipment_data['transport_mode'],
            sum(p['weight'] for p in shipment_data['packages'])
        ),
        rur=scorer.calculate_rur(
            shipment_data['packages'],
            {'volume': 67.6, 'max_weight': 26755}  # Standard container
        ),
        eer=scorer.calculate_eer(
            shipment_data['transport_mode'],
            pipeline._calculate_distance(
                shipment_data['origin'],
                shipment_data['destination']
            ),
            sum(p['weight'] for p in shipment_data['packages'])
        ),
        wrs=scorer.calculate_wrs(shipment_data['packages'])
    )
    
    overall_score = scorer.calculate_overall_score(metrics)
    predictions = predictor.predict_sustainability(shipment_data)
    
    return {
        'metrics': {
            'package_sustainability_index': metrics.psi,
            'route_efficiency_score': metrics.res,
            'carbon_emission_index': metrics.cei,
            'resource_utilization_rate': metrics.rur,
            'energy_efficiency_rating': metrics.eer,
            'waste_reduction_score': metrics.wrs
        },
        'overall_sustainability_score': overall_score,
        'predictions': predictions,
        'processed_data': processed_data
    }