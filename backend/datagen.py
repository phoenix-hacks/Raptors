import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple
import random
from dataclasses import dataclass

@dataclass
class LocationCluster:
    """Represents a cluster of locations (e.g., major city hub)"""
    name: str
    lat: float
    long: float
    radius: float  # radius in degrees

class SyntheticDataGenerator:
    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        self.start_date = start_date or datetime(2023, 1, 1)
        self.end_date = end_date or datetime(2024, 1, 1)
        
        # Define common shipping hubs/clusters
        self.location_clusters = [
            # Major US logistics hubs
            LocationCluster("New York", 40.7128, -74.0060, 2.0),
            LocationCluster("Los Angeles", 34.0522, -118.2437, 2.0),
            LocationCluster("Chicago", 41.8781, -87.6298, 1.5),
            LocationCluster("Houston", 29.7604, -95.3698, 1.5),
            LocationCluster("Miami", 25.7617, -80.1918, 1.0),
            LocationCluster("Seattle", 47.6062, -122.3321, 1.0),
            # Add more clusters as needed
        ]
        
        # Define realistic constraints
        self.transport_modes = {
            'truck': 0.5,    # probability weights
            'train': 0.2,
            'ship': 0.2,
            'air': 0.1
        }
        
        self.material_types = {
            'cardboard': 0.4,
            'paper': 0.2,
            'plastic': 0.2,
            'metal': 0.1,
            'glass': 0.05,
            'wood': 0.05
        }
        
        # Define realistic package size constraints
        self.size_categories = {
            'small': {'weight': (0.1, 5), 'dims': (5, 30)},
            'medium': {'weight': (5, 20), 'dims': (20, 60)},
            'large': {'weight': (20, 100), 'dims': (50, 120)}
        }

    def _generate_location_near_cluster(self) -> Tuple[float, float]:
        """Generate location near a random cluster"""
        cluster = np.random.choice(self.location_clusters)
        
        # Generate random offset within cluster radius
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(0, cluster.radius)
        
        lat = cluster.lat + (distance * np.cos(angle))
        long = cluster.long + (distance * np.sin(angle))
        
        return lat, long

    def _generate_package(self, timestamp: datetime) -> Dict:
        """Generate a single package with realistic properties"""
        # Select size category with seasonal variation
        month = timestamp.month
        # Increase probability of larger packages during holiday seasons
        is_holiday_season = month in [11, 12]
        size_probs = [0.4, 0.4, 0.2] if not is_holiday_season else [0.3, 0.3, 0.4]
        size_category = np.random.choice(list(self.size_categories.keys()), p=size_probs)
        size_constraints = self.size_categories[size_category]
        
        # Generate dimensions with some correlation
        base_dim = np.random.uniform(*size_constraints['dims'])
        length = base_dim * np.random.uniform(0.8, 1.2)
        width = base_dim * np.random.uniform(0.6, 1.0)
        height = base_dim * np.random.uniform(0.4, 0.8)
        
        # Generate correlated weight
        volume = length * width * height
        density = np.random.uniform(0.01, 0.05)  # g/cm³
        weight = volume * density
        
        # Adjust weight to be within category constraints
        weight = np.clip(weight, *size_constraints['weight'])
        
        # Select material type with some business logic
        if weight > 50:  # Heavy items more likely to be metal/wood
            material_weights = {'metal': 0.4, 'wood': 0.3, 'cardboard': 0.2, 'plastic': 0.1}
        else:
            material_weights = self.material_types
        
        material = np.random.choice(
            list(material_weights.keys()),
            p=[material_weights[k] for k in material_weights.keys()]
        )
        
        # Determine recyclability based on material and current trends
        base_recyclable_prob = {
            'cardboard': 0.95,
            'paper': 0.90,
            'plastic': 0.60,
            'metal': 0.85,
            'glass': 0.90,
            'wood': 0.70
        }
        
        # Increase recyclability probability over time
        time_factor = (timestamp - self.start_date).days / (self.end_date - self.start_date).days
        recyclable_prob = min(1.0, base_recyclable_prob[material] + (0.2 * time_factor))
        
        return {
            'package_id': f'PKG{np.random.randint(10000, 99999)}',
            'material_type': material,
            'weight': round(weight, 2),
            'dimensions': {
                'length': round(length, 2),
                'width': round(width, 2),
                'height': round(height, 2)
            },
            'recyclable': np.random.random() < recyclable_prob
        }

    def _select_transport_mode(self, distance: float, weight: float, 
                             timestamp: datetime) -> str:
        """Select appropriate transport mode based on distance, weight, and time"""
        if distance < 300:  # Short distance
            probs = {'truck': 0.8, 'train': 0.15, 'ship': 0.0, 'air': 0.05}
        elif distance < 1000:  # Medium distance
            probs = {'truck': 0.4, 'train': 0.4, 'ship': 0.1, 'air': 0.1}
        else:  # Long distance
            probs = {'truck': 0.2, 'train': 0.3, 'ship': 0.4, 'air': 0.1}
        
        # Adjust for weight
        if weight > 1000:  # Heavy shipment
            probs['air'] = 0.05
            probs['ship'] *= 1.5
        
        # Adjust for urgency (simplified: assume end of month/quarter is more urgent)
        if timestamp.day > 25 or timestamp.month in [3, 6, 9, 12]:
            probs['air'] *= 1.5
            probs['truck'] *= 1.2
        
        # Normalize probabilities
        total = sum(probs.values())
        probs = {k: v/total for k, v in probs.items()}
        
        return np.random.choice(list(probs.keys()), p=list(probs.values()))

    def generate_shipment(self, timestamp: datetime = None) -> Dict:
        """Generate a single shipment with realistic properties"""
        if timestamp is None:
            timestamp = np.random.choice(
                pd.date_range(self.start_date, self.end_date, freq='H')
            ).to_pydatetime()
        
        # Generate origin and destination
        origin_lat, origin_long = self._generate_location_near_cluster()
        dest_lat, dest_long = self._generate_location_near_cluster()
        
        # Generate 1-5 packages, with more packages during peak seasons
        is_peak_season = timestamp.month in [11, 12]  # Holiday season
        num_packages = np.random.randint(1, 6 if is_peak_season else 4)
        
        packages = [self._generate_package(timestamp) for _ in range(num_packages)]
        
        # Calculate total weight for transport mode selection
        total_weight = sum(p['weight'] for p in packages)
        
        # Calculate approximate distance
        distance = np.sqrt(
            (dest_lat - origin_lat)**2 + (dest_long - origin_long)**2
        ) * 111  # Convert to km (approximate)
        
        # Select transport mode based on characteristics
        transport_mode = self._select_transport_mode(distance, total_weight, timestamp)
        
        return {
            'shipment_id': f'SHIP{np.random.randint(100000, 999999)}',
            'timestamp': timestamp.isoformat(),
            'origin': {'lat': origin_lat, 'long': origin_long},
            'destination': {'lat': dest_lat, 'long': dest_long},
            'transport_mode': transport_mode,
            'packages': packages
        }

    def generate_historical_dataset(self, num_shipments: int) -> Tuple[List[Dict], List[float]]:
        """Generate historical dataset with shipments and corresponding sustainability scores"""
        shipments = []
        scores = []
        
        # Generate timestamps with realistic patterns
        # More shipments during business hours and weekdays
        timestamps = []
        current = self.start_date
        while len(timestamps) < num_shipments:
            if current.weekday() < 5:  # Weekday
                if 8 <= current.hour <= 18:  # Business hours
                    timestamps.append(current)
            elif np.random.random() < 0.3:  # Weekend with lower probability
                timestamps.append(current)
            current += timedelta(hours=1)
            if current > self.end_date:
                current = self.start_date
        
        timestamps = np.random.choice(timestamps, num_shipments, replace=False)
        timestamps.sort()
        
        for timestamp in timestamps:
            shipment = self.generate_shipment(timestamp)
            shipments.append(shipment)
            
            # Generate realistic sustainability score based on shipment characteristics
            base_score = 70  # Base sustainability score
            
            # Adjust score based on transport mode
            transport_factors = {
                'truck': -5,
                'train': +5,
                'ship': 0,
                'air': -15
            }
            score = base_score + transport_factors[shipment['transport_mode']]
            
            # Adjust for package characteristics
            for package in shipment['packages']:
                if package['recyclable']:
                    score += 2
                if package['material_type'] in ['cardboard', 'paper']:
                    score += 1
                elif package['material_type'] in ['plastic']:
                    score -= 1
            
            # Add some random variation
            score += np.random.normal(0, 3)
            
            # Ensure score is within bounds
            score = np.clip(score, 0, 100)
            scores.append(score)
        
        return shipments, scores

def save_synthetic_data(num_shipments: int = 1000, output_file: str = 'synthetic_data.json'):
    """Generate and save synthetic data to file"""
    generator = SyntheticDataGenerator()
    shipments, scores = generator.generate_historical_dataset(num_shipments)
    
    output = {
        'metadata': {
            'num_shipments': num_shipments,
            'date_generated': datetime.now().isoformat(),
            'date_range': {
                'start': generator.start_date.isoformat(),
                'end': generator.end_date.isoformat()
            }
        },
        'data': {
            'shipments': shipments,
            'sustainability_scores': scores
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {num_shipments} synthetic shipments and saved to {output_file}")
    
    # Print some basic statistics
    print("\nDataset Statistics:")
    print(f"Average sustainability score: {np.mean(scores):.2f}")
    print(f"Score range: {min(scores):.2f} - {max(scores):.2f}")
    
    transport_modes = [s['transport_mode'] for s in shipments]
    print("\nTransport mode distribution:")
    for mode in set(transport_modes):
        count = transport_modes.count(mode)
        print(f"{mode}: {count/len(transport_modes)*100:.1f}%")

if __name__ == "__main__":
    save_synthetic_data(num_shipments=1000)