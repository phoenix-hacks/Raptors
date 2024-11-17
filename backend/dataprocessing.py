from dataclasses import Field
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, validator
import logging
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PackageData(BaseModel):
    package_id: str
    material_type: str
    weight: float
    dimensions: Dict[str, float]
    recyclable: bool

    # @validator('weight')
    # def validate_weight(cls, v):
    #     if v <= 0:
    #         raise ValueError('Weight must be positive')
    #     return v

class ShipmentData(BaseModel):
    shipment_id: str
    origin: Dict[str, float]  # lat, long
    destination: Dict[str, float]
    transport_mode: str
    packages: List[PackageData]
    timestamp: Optional[datetime]

class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: Union[dict, pd.DataFrame]):
        pass

    @abstractmethod
    def validate(self, data: Union[dict, pd.DataFrame]) -> bool:
        pass

# Data Processing Pipeline
class LogisticsSustainabilityPipeline:
    def __init__(self):
        self.processors: List[DataProcessor] = []
        self.error_handlers: Dict[str, callable] = {}
        self.enrichment_sources: Dict[str, callable] = {}

    def add_processor(self, processor: DataProcessor):
        self.processors.append(processor)

    def add_error_handler(self, error_type: str, handler: callable):
        self.error_handlers[error_type] = handler

    def add_enrichment_source(self, source_name: str, source_callable: callable):
        self.enrichment_sources[source_name] = source_callable

    def process_data(self, raw_data: Union[dict, pd.DataFrame]) -> Dict:
        try:
            # 1. Initial Validation
            validated_data =  self._validate_data(raw_data)
            
            # 2. Data Enrichment
            enriched_data =  self._enrich_data(validated_data)
            
            # 3. Process through pipeline
            processed_data =  self._run_processors(enriched_data)
            
            # 4. Generate Analytics
            analytics_results =  self._generate_analytics(processed_data)
            
            return {
                'status': 'success',
                'processed_data': processed_data,
                'analytics': analytics_results
            }
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _validate_data(self, data: Union[dict, pd.DataFrame]) -> Union[dict, pd.DataFrame]:
        """Validate incoming data structure and content"""
        try:
            if isinstance(data, dict):
                ShipmentData(**data)
            elif isinstance(data, pd.DataFrame):
                # Validate required columns
                required_columns = {'shipment_id', 'origin', 'destination', 'transport_mode'}
                if not required_columns.issubset(data.columns):
                    raise ValueError(f"Missing required columns: {required_columns - set(data.columns)}")
            return data
        except Exception as e:
            if type(e).__name__ in self.error_handlers:
                return self.error_handlers[type(e).__name__](e, data)
            raise

    def _enrich_data(self, data: Union[dict, pd.DataFrame]) -> Dict:
        """Enrich data with additional information from various sources"""
        enriched_data = data.copy() if isinstance(data, dict) else data.to_dict('records')[0]
        
        # Parallel enrichment processing
        with ThreadPoolExecutor() as executor:
            enrichment_futures = {
                source_name: executor.submit(source_callable, enriched_data)
                for source_name, source_callable in self.enrichment_sources.items()
            }
            
            # Collect results
            for source_name, future in enrichment_futures.items():
                try:
                    enriched_data[source_name] = future.result()
                except Exception as e:
                    logger.error(f"Error enriching data from {source_name}: {str(e)}")
                    
        return enriched_data

    def _run_processors(self, data: Dict) -> Dict:
        """Run data through all processors in sequence"""
        processed_data = data
        for processor in self.processors:
            if processor.validate(processed_data):
                processed_data = processor.process(processed_data)
            else:
                logger.warning(f"Data validation failed for processor: {processor.__class__.__name__}")
        return processed_data

    def _generate_analytics(self, data: Dict) -> Dict:
        """Generate analytics from processed data"""
        return {
            'sustainability_metrics': self._calculate_sustainability_metrics(data),
            'optimization_opportunities': self._identify_optimization_opportunities(data),
            'trend_analysis': self._analyze_trends(data)
        }

    def _calculate_sustainability_metrics(self, data: Dict) -> Dict:
        """Calculate various sustainability metrics"""
        return {
            'carbon_footprint': self._calculate_carbon_footprint(data),
            'resource_efficiency': self._calculate_resource_efficiency(data),
            'waste_reduction': self._calculate_waste_reduction(data),
            'energy_efficiency': self._calculate_energy_efficiency(data)
        }

    def _calculate_carbon_footprint(self, data: Dict) -> float:
        """Calculate carbon footprint based on shipment data"""
        # Example calculation - would be more complex in production
        distance = self._calculate_distance(data['origin'], data['destination'])
        transport_emissions = {
            'truck': 0.1,  # kg CO2 per km
            'train': 0.04,
            'ship': 0.02,
            'air': 0.5
        }
        return distance * transport_emissions.get(data['transport_mode'], 0.1)

    def _calculate_resource_efficiency(self, data: Dict) -> float:
        """Calculate resource efficiency score based on packaging and transport utilization"""
        try:
            packages = data.get('packages', [])
            if not packages:
                return 0.0

            # Calculate volume utilization
            total_volume = sum(
                dim.get('length', 0) * dim.get('width', 0) * dim.get('height', 0)
                for package in packages
                for dim in [package.get('dimensions', {})]
            )

            # Calculate weight utilization
            total_weight = sum(package.get('weight', 0) for package in packages)

            # Standard container metrics (example values)
            standard_container = {
                'volume': 67.6,  # m³ (standard 40ft container)
                'max_weight': 26755  # kg (standard 40ft container max payload)
            }

            # Calculate utilization ratios
            volume_utilization = min(total_volume / standard_container['volume'], 1.0)
            weight_utilization = min(total_weight / standard_container['max_weight'], 1.0)

            # Material efficiency (percentage of recyclable packages)
            material_efficiency = sum(1 for p in packages if p.get('recyclable', False)) / len(packages)

            # Weighted score (can be adjusted based on importance)
            resource_efficiency = (
                volume_utilization * 0.4 +
                weight_utilization * 0.3 +
                material_efficiency * 0.3
            ) * 100  # Convert to percentage

            return round(resource_efficiency, 2)

        except Exception as e:
            logger.error(f"Error calculating resource efficiency: {str(e)}")
            return 0.0

    def _calculate_waste_reduction(self, data: Dict) -> float:
        """Calculate waste reduction metrics based on packaging and materials"""
        try:
            packages = data.get('packages', [])
            if not packages:
                return 0.0

            # Define material recycling rates
            material_recycling_rates = {
                'cardboard': 0.85,
                'paper': 0.80,
                'plastic': 0.30,
                'metal': 0.90,
                'glass': 0.75,
                'wood': 0.60
            }

            # Calculate waste reduction score
            total_score = 0
            for package in packages:
                material_type = package.get('material_type', '').lower()
                weight = package.get('weight', 0)
                
                # Base score from material recyclability
                material_score = material_recycling_rates.get(material_type, 0.1)
                
                # Adjust for package properties
                if package.get('recyclable', False):
                    material_score *= 1.2  # 20% bonus for recyclable packaging
                
                # Volume efficiency (penalize oversized packaging)
                dimensions = package.get('dimensions', {})
                volume = dimensions.get('length', 0) * dimensions.get('width', 0) * dimensions.get('height', 0)
                density = weight / volume if volume > 0 else 0
                if density < 0.1:  # Example threshold for inefficient packaging
                    material_score *= 0.8  # 20% penalty for inefficient volume usage
                
                total_score += material_score * weight

            # Normalize score to 0-100 range
            normalized_score = (total_score / (sum(p.get('weight', 0) for p in packages))) * 100
            return round(normalized_score, 2)

        except Exception as e:
            logger.error(f"Error calculating waste reduction: {str(e)}")
            return 0.0

    def _calculate_energy_efficiency(self, data: Dict) -> float:
        """Calculate energy efficiency metrics based on transport mode and distance"""
        try:
            # Energy efficiency factors (MJ/tonne-km) for different transport modes
            energy_factors = {
                'truck': 2.5,
                'train': 0.6,
                'ship': 0.2,
                'air': 8.0
            }

            transport_mode = data.get('transport_mode', 'truck').lower()
            distance = self._calculate_distance(data['origin'], data['destination'])
            total_weight = sum(p.get('weight', 0) for p in data.get('packages', []))
            
            # Convert weight to tonnes
            weight_tonnes = total_weight / 1000
            
            # Calculate base energy consumption
            base_energy = distance * weight_tonnes * energy_factors.get(transport_mode, 2.5)
            
            # Calculate efficiency score (inverse relationship - lower energy use is better)
            max_energy = distance * weight_tonnes * max(energy_factors.values())
            min_energy = distance * weight_tonnes * min(energy_factors.values())
            
            if max_energy == min_energy:
                return 100.0
            
            efficiency_score = (1 - (base_energy - min_energy) / (max_energy - min_energy)) * 100
            return round(efficiency_score, 2)

        except Exception as e:
            logger.error(f"Error calculating energy efficiency: {str(e)}")
            return 0.0

    def _calculate_distance(self, origin: Dict[str, float], destination: Dict[str, float]) -> float:
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

    def _identify_optimization_opportunities(self, data: Dict) -> List[Dict]:
        """Identify potential areas for optimization"""
        opportunities = []
        
        # Check for route optimization
        if self._can_optimize_route(data):
            opportunities.append({
                'type': 'route_optimization',
                'potential_impact': 'high',
                'description': 'Alternative route could reduce distance by 15%'
            })
            
        # Check for packaging optimization
        if self._can_optimize_packaging(data):
            opportunities.append({
                'type': 'packaging_optimization',
                'potential_impact': 'medium',
                'description': 'Using recyclable materials could reduce waste by 25%'
            })
            
        return opportunities

    def _analyze_trends(self, data: Dict) -> Dict:
        """Analyze trends in the data"""
        return {
            'historical_comparison': self._compare_historical_data(data),
            'seasonal_patterns': self._identify_seasonal_patterns(data),
            'anomalies': self._detect_anomalies(data)
        }
    
    def _can_optimize_route(self, data: Dict) -> bool:
        """
        Check if route can be optimized
        This needs to be improved
        """
        # Example optimization check 
        # You could add more complex logic here
        distance = self._calculate_distance(data['origin'], data['destination'])
        return distance > 500  # Example: suggest optimization for routes over 500 km

    def _can_optimize_packaging(self, data: Dict) -> bool:
        """
        Check if packaging can be optimized.
        This also needs to be improved
        """
        # Check packaging efficiency
        packages = data.get('packages', [])
        
        # Example checks:
        # 1. Check if any non-recyclable packages exist
        non_recyclable_packages = [p for p in packages if not p.get('recyclable', False)]
        
        # 2. Check if packages are inefficiently sized
        oversized_packages = [p for p in packages if any(
            dim > 50 for dim in p.get('dimensions', {}).values()
        )]
        
        return bool(non_recyclable_packages or oversized_packages)
    
    def _identify_seasonal_patterns(self, data: Dict) -> Dict:
        """Identify seasonal patterns in shipping data"""
        try:
            timestamp = data.get('timestamp')
            if not timestamp:
                return {'season': 'unknown', 'patterns': []}

            month = timestamp.month
            seasons = {
                (12, 1, 2): 'winter',
                (3, 4, 5): 'spring',
                (6, 7, 8): 'summer',
                (9, 10, 11): 'fall'
            }
            current_season = next(
                season for months, season in seasons.items() if month in months
            )

            # Example seasonal patterns (would be based on historical data in production) TODO: 
            seasonal_impacts = {
                'winter': [
                    {'factor': 'weather_delays', 'impact': 'high'},
                    {'factor': 'energy_consumption', 'impact': 'high'},
                    {'factor': 'route_restrictions', 'impact': 'medium'}
                ],
                'summer': [
                    {'factor': 'cooling_requirements', 'impact': 'high'},
                    {'factor': 'traffic_congestion', 'impact': 'medium'},
                    {'factor': 'delivery_windows', 'impact': 'low'}
                ],
                'spring': [
                    {'factor': 'route_flexibility', 'impact': 'high'},
                    {'factor': 'energy_consumption', 'impact': 'medium'},
                    {'factor': 'delivery_efficiency', 'impact': 'high'}
                ],
                'fall': [
                    {'factor': 'weather_variability', 'impact': 'medium'},
                    {'factor': 'route_optimization', 'impact': 'high'},
                    {'factor': 'delivery_volume', 'impact': 'medium'}
                ]
            }

            return {
                'season': current_season,
                'patterns': seasonal_impacts.get(current_season, [])
            }

        except Exception as e:
            logger.error(f"Error identifying seasonal patterns: {str(e)}")
            return {'season': 'unknown', 'patterns': []}

    def _detect_anomalies(self, data: Dict) -> List:
        """Detect anomalies in shipping patterns and sustainability metrics"""
        try:
            anomalies = []
            
            # Check distance anomalies
            distance = self._calculate_distance(data['origin'], data['destination'])
            if distance > 1000:  # Example threshold
                anomalies.append({
                    'type': 'distance',
                    'severity': 'high',
                    'description': 'Unusually long shipping distance detected',
                    'recommendation': 'Consider regional fulfillment centers'
                })

            # Check packaging anomalies
            packages = data.get('packages', [])
            for package in packages:
                weight = package.get('weight', 0)
                dimensions = package.get('dimensions', {})
                volume = dimensions.get('length', 0) * dimensions.get('width', 0) * dimensions.get('height', 0)
                
                # Density check
                if volume > 0 and (weight / volume) < 0.01:
                    anomalies.append({
                        'type': 'packaging',
                        'severity': 'medium',
                        'description': f'Inefficient packaging detected for package {package.get("package_id")}',
                        'recommendation': 'Review packaging size optimization'
                    })

            # Transport mode anomalies
            transport_mode = data.get('transport_mode')
            if transport_mode == 'air' and distance < 300:
                anomalies.append({
                    'type': 'transport',
                    'severity': 'high',
                    'description': 'Air transport used for short distance',
                    'recommendation': 'Consider ground transportation alternatives'
                })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []

    def _compare_historical_data(self, data: Dict) -> Dict:
        """Compare current shipment with historical data for trend analysis"""
        try:
            # In production, this would query a database for historical data
            # For demonstration, we'll create example comparisons
            current_metrics = self._calculate_sustainability_metrics(data)
            
            return {
                'comparison_status': 'completed',
                'metrics_comparison': {
                    'carbon_footprint': {
                        'current': current_metrics['carbon_footprint'],
                        'historical_avg': 150.0,  # Example value
                        'trend': 'improving' if current_metrics['carbon_footprint'] < 150.0 else 'declining'
                    },
                    'resource_efficiency': {
                        'current': current_metrics['resource_efficiency'],
                        'historical_avg': 75.0,  # Example value
                        'trend': 'improving' if current_metrics['resource_efficiency'] > 75.0 else 'declining'
                    },
                    'trends': [
                        {
                            'metric': 'carbon_efficiency',
                            'period': 'last_30_days',
                            'change_percentage': -5.2  # Example value
                        },
                        {
                            'metric': 'packaging_efficiency',
                            'period': 'last_30_days',
                            'change_percentage': 3.8  # Example value
                        }
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error comparing historical data: {str(e)}")
            return {'comparison_status': 'failed', 'error': str(e)}


# Example Usage
def run_pipeline():
    # Create pipeline instance
    pipeline = LogisticsSustainabilityPipeline()
    
    # Add custom processors
    class CarbonFootprintProcessor(DataProcessor):
        def process(self, data):
            # Process carbon footprint calculations
            return data
            
        def validate(self, data):
            return True
            
    pipeline.add_processor(CarbonFootprintProcessor())
    
    # Add enrichment sources
    def weather_enrichment(data):
        # Fetch weather data for route
        return {'weather_conditions': 'sunny'}
        
    pipeline.add_enrichment_source('weather', weather_enrichment)
    
    # Sample data
    sample_data = {
        'shipment_id': 'SHIP123',
        'origin': {'lat': 40.7128, 'long': -74.0060},
        'destination': {'lat': 34.0522, 'long': -118.2437},
        'transport_mode': 'truck',
        'packages': [{
            'package_id': 'PKG1',
            'material_type': 'cardboard',
            'weight': 10.5,
            'dimensions': {'length': 20, 'width': 15, 'height': 10},
            'recyclable': True
        }],
        'timestamp': datetime.now()
    }
    
    # Process data
    result = pipeline.process_data(sample_data)
    return result

import json

if __name__ == "__main__":
    def main():
        result = run_pipeline()
        
        print("Pipeline Processing Result:")
        print("------------------------")
        # Use json.dumps() to pretty print with indentation
        print(json.dumps(result, indent=2, default=str))
    
    main()