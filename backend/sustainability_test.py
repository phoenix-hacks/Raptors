from datetime import datetime
import json
from typing import List, Dict
import pandas as pd
import numpy as np
from pprint import pprint

from sustainability_scoring import (
    LogisticsSustainabilityPipeline,
    SustainabilityScoring,
    SustainabilityPredictor,
    analyze_sustainability
)

def generate_sample_data(num_samples: int = 10) -> List[Dict]:
    """Generate sample shipment data for testing"""
    
    transport_modes = ['truck', 'train', 'ship', 'air']
    material_types = ['cardboard', 'paper', 'plastic', 'metal', 'glass', 'wood']
    
    samples = []
    for i in range(num_samples):
        # Generate random coordinates within continental US
        origin_lat = np.random.uniform(25, 48)
        origin_long = np.random.uniform(-123, -71)
        dest_lat = np.random.uniform(25, 48)
        dest_long = np.random.uniform(-123, -71)
        
        # Generate 1-3 packages per shipment
        num_packages = np.random.randint(1, 4)
        packages = []
        for j in range(num_packages):
            length = np.random.uniform(10, 100)
            width = np.random.uniform(10, 100)
            height = np.random.uniform(10, 100)
            
            package = {
                'package_id': f'PKG{i}-{j}',
                'material_type': np.random.choice(material_types),
                'weight': np.random.uniform(0.5, 50),  # kg
                'dimensions': {
                    'length': length,
                    'width': width,
                    'height': height
                },
                'recyclable': np.random.choice([True, False], p=[0.7, 0.3])
            }
            packages.append(package)
        
        shipment = {
            'shipment_id': f'SHIP{i}',
            'origin': {'lat': origin_lat, 'long': origin_long},
            'destination': {'lat': dest_lat, 'long': dest_long},
            'transport_mode': np.random.choice(transport_modes),
            'packages': packages,
            'timestamp': datetime.now()
        }
        samples.append(shipment)
    
    return samples

def test_sustainability_scoring():
    """Test the sustainability scoring system"""
    
    pipeline = LogisticsSustainabilityPipeline()
    predictor = SustainabilityPredictor()
    print("\nGenerating sample shipment data...")
    sample_shipments = generate_sample_data(10)
    
    # historical data for ML training. TODO: replace with real data
    print("\nGenerating historical data for ML training...")
    historical_data = generate_sample_data(100)

    # mock historical sustainability scores
    historical_scores = np.random.uniform(50, 95, size=100)
    
    # Train model
    print("\nTraining ML model...")
    training_results = predictor.train(historical_data, historical_scores)
    print(f"Model Training Results:")
    print(f"Training Score: {training_results['train_score']:.2f}")
    print(f"Test Score: {training_results['test_score']:.2f}")
    
    # Analyze sample shipments
    print("\nAnalyzing sample shipments...")
    results = []
    for shipment in sample_shipments[:3]:  # Analyze first 3 shipments for demonstration
        print(f"\nAnalyzing shipment {shipment['shipment_id']}:")
        print("----------------------------------------")
        
        # Analyze sustainability using the trained predictor
        analysis = analyze_sustainability(pipeline, shipment, predictor)
        
        print("\nMetrics:")
        for metric, value in analysis['metrics'].items():
            print(f"{metric}: {value:.2f}")
        
        print(f"\nOverall Sustainability Score: {analysis['overall_sustainability_score']:.2f}")
        
        print("\nML Predictions:")
        print(f"Predicted Sustainability Score: {analysis['predictions']['predicted_score']:.2f}")
        
        print("\nFeature Importances:")
        for feature, importance in analysis['predictions']['feature_importances'].items():
            print(f"{feature}: {importance:.3f}")
        
        results.append(analysis)
    
    print("\nSummary Statistics:")
    print("----------------------------------------")
    scores = [r['overall_sustainability_score'] for r in results]
    predictions = [r['predictions']['predicted_score'] for r in results]
    
    print(f"Average Sustainability Score: {np.mean(scores):.2f}")
    print(f"Average Predicted Score: {np.mean(predictions):.2f}")
    print(f"Score Range: {min(scores):.2f} - {max(scores):.2f}")
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'num_shipments_analyzed': len(results),
        'summary_statistics': {
            'avg_sustainability_score': float(np.mean(scores)),
            'avg_predicted_score': float(np.mean(predictions)),
            'min_score': float(min(scores)),
            'max_score': float(max(scores))
        },
        'detailed_results': results
    }
    
    with open('sustainability_analysis_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\nResults saved to 'sustainability_analysis_results.json'")
def analyze_results():
    """Analyze and visualize the results"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        with open('sustainability_analysis_results.json', 'r') as f:
            results = json.load(f)
        
        metrics_data = []
        for r in results['detailed_results']:
            metrics_data.append(r['metrics'])
        df = pd.DataFrame(metrics_data)
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df)
        plt.xticks(rotation=45)
        plt.title('Distribution of Sustainability Metrics')
        plt.tight_layout()
        plt.savefig('sustainability_metrics_distribution.png')
        print("\nVisualization saved as 'sustainability_metrics_distribution.png'")
        
    except ImportError:
        print("\nNote: matplotlib and seaborn are required for visualization.")
        print("Install them using: pip install matplotlib seaborn")

if __name__ == "__main__":
    print("Starting Sustainability Scoring System Test...")
    test_sustainability_scoring()
    # print("\nAnalyzing results...")
    # analyze_results()
