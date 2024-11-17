from functools import wraps
import json
import time
from flask import Flask, request, jsonify
from typing import Dict, Any
import pandas as pd
import os
from datetime import datetime
from io import StringIO
import traceback
import requests
from config import API_KEY
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from supabase import create_client, Client
import datetime
import jwt
from flask_cors import CORS
from supascript import push_sustainability_data
from supabase_client import supabase

load_dotenv('.env.local')
url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
service_role_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
jwt_secret: str = os.environ.get("SUPABASE_JWT_SECRET")

supabase: Client = create_client(url, service_role_key)

from sustainability_scoring import (
    LogisticsSustainabilityPipeline,
    SustainabilityPredictor,
    analyze_sustainability
)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins='http://localhost:3000')

@app.after_request
def after_request(response):
    return response

# Initialize components
pipeline = LogisticsSustainabilityPipeline()
predictor = SustainabilityPredictor()

client = InferenceClient(api_key=API_KEY)

def get_llm_analysis(metrics: Dict[str, float], overall_score: float) -> str:
    """Get LLM analysis of sustainability metrics"""
    
    prompt = f"""Analyze the following logistics sustainability metrics and provide specific recommendations for improvement:

Metrics:
- Package Sustainability Index: {metrics['package_sustainability_index']:.2f}
- Route Efficiency Score: {metrics['route_efficiency_score']:.2f}
- Carbon Emission Index: {metrics['carbon_emission_index']:.2f}
- Resource Utilization Rate: {metrics['resource_utilization_rate']:.2f}
- Energy Efficiency Rating: {metrics['energy_efficiency_rating']:.2f}
- Waste Reduction Score: {metrics['waste_reduction_score']:.2f}

Overall Sustainability Score: {overall_score:.2f}

Please provide:
1. A brief analysis of the strongest and weakest areas
2. Three specific, actionable recommendations for improvement
3. Potential environmental impact of these improvements
"""

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-1B-Instruct",
        messages=[
            { "role": "user", "content": f"{prompt}" }
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    
    return response.choices[0].message.content

from flask import request, jsonify

@app.route('/api/v1/chat', methods=['POST', 'GET'])
def chat_with_llm():
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'No message content provided'}), 400
            
        user_message = data['content']
        session_id = data.get('session_id')
        
        prompt = """ You are a sustainability and logistics expert AI assistant. 
                 Focus on providing accurate, actionable insights about environmental impact, carbon footprint, 
                 and sustainable practices. Use concrete metrics and specific examples when possible."""

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        llm_reply = response.choices[0].message.content

        return jsonify({
            'reply': llm_reply,
            'session_id': session_id
        }), 200

    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200

        # Existing token validation code
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            decoded = jwt.decode(
                        token,
                        jwt_secret,
                        algorithms=["HS256"],
                        audience="authenticated"
                    )
            user_id = decoded.get("sub")
            if not user_id:
                raise jwt.InvalidTokenError("User ID not found in token.")
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401

        return f(user_id, *args, **kwargs)

    return decorated

import csv
import math

def replace_nan(obj):
    """
    Recursively replace NaN values in a nested structure with None.
    """
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(item) for item in obj]
    elif isinstance(obj, float):
        return None if math.isnan(obj) else obj
    else:
        return obj

@app.route('/api/v1/sustainability/upload', methods=['POST', 'OPTIONS'])
@token_required
def upload_csv(user_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        if 'file' not in request.files:
            app.logger.error('No file part in the request')
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            app.logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        # Read CSV file into pandas DataFrame
        csv_content = StringIO(file.stream.read().decode("UTF-8"))
        df = pd.read_csv(csv_content)

        # Validate required columns
        required_columns = [
            "shipment_id", "timestamp",
            "origin_lat", "origin_long",
            "destination_lat", "destination_long",
            "transport_mode", "packages",
            "sustainability_score"
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            app.logger.error(f'Missing required columns: {missing_columns}')
            return jsonify({'error': 'Missing required columns', 'missing_columns': missing_columns}), 400

        # Convert DataFrame to required format
        shipments = []
        sustainability_scores = []

        for index, row in df.iterrows():
            try:
                # Parse packages field from JSON string to list
                if isinstance(row["packages"], str):
                    packages = json.loads(row["packages"])
                elif isinstance(row["packages"], list):
                    packages = row["packages"]
                else:
                    raise ValueError("Invalid format for packages field")

                shipment = {
                    "shipment_id": row["shipment_id"],
                    "timestamp": row["timestamp"],
                    "origin": {
                        "lat": row["origin_lat"],
                        "long": row["origin_long"]
                    },
                    "destination": {
                        "lat": row["destination_lat"],
                        "long": row["destination_long"]
                    },
                    "transport_mode": row["transport_mode"],
                    "packages": packages
                }
                shipments.append(shipment)
                sustainability_scores.append(row["sustainability_score"])
            except (ValueError, json.JSONDecodeError) as e:
                app.logger.error(f"Row parsing error at index {index}: {str(e)}")
                return jsonify({'error': 'Invalid data format in CSV', 'row_index': index}), 400

        data = {
            "shipments": shipments,
            "sustainability_scores": sustainability_scores
        }

        # Train the model
        train_result = train_model()

        if isinstance(train_result, tuple):
            response_data, status_code = train_result
            if status_code != 200:
                return jsonify({
                    'error': 'Training failed',
                    'details': str(response_data)
                }), status_code

            if hasattr(response_data, 'get_json'):
                response_data = response_data.get_json()

            batch_analysis_result = perform_batch_analysis({"shipments": shipments})
            if isinstance(batch_analysis_result, tuple):
                return batch_analysis_result  # Error response
            else:
                # Prepare the response data
                response_payload = {
                    "batch_analysis": batch_analysis_result
                }

                # Replace NaN values with None
                safe_response = replace_nan(response_payload)

                # Push the entire JSON payload to Supabase
                try:
                    push_sustainability_data(safe_response, user_id)
                except Exception as e:
                    app.logger.error(f"Error pushing data to Supabase: {str(e)}")
                    return jsonify({
                        'error': 'Failed to push data to Supabase',
                        'details': str(e)
                    }), 500

                # Return the safe_response as JSON
                return jsonify(safe_response), 200
        else:
            app.logger.error(f"Invalid train_result type: {type(train_result)}")
            return jsonify({'error': 'Invalid response from training model'}), 500

    except KeyError as e:
        # Specific handling for KeyError
        app.logger.error(f"Upload error: {e}")
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Upload error: {e}")
        response = jsonify({'error': str(e)})
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response

@app.route('/api/v1/sustainability/analyze', methods=['POST'])
def analyze_shipment():
    """Analyze shipment sustainability with LLM-enhanced insights"""
    try:
        data = request.get_json()

        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.datetime.now().isoformat()
        
        # Validate required fields
        required_fields = ['shipment_id', 'origin', 'destination', 'transport_mode', 'packages']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required_fields': required_fields
            }), 400
            
        # Perform sustainability analysis
        analysis_results = analyze_sustainability(pipeline, data, predictor)
        
        # Get LLM analysis
        llm_insights = get_llm_analysis(
            analysis_results['metrics'],
            analysis_results['overall_sustainability_score']
        )
        
        # Combine results
        response = {
            'timestamp': datetime.datetime.now().isoformat(),
            'shipment_id': data['shipment_id'],
            'sustainability_analysis': analysis_results,
            'llm_insights': llm_insights,
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/v1/sustainability/train', methods=['POST'])
def train_model():
    """Train the sustainability predictor with historical data"""
    try:
        json_file_path = os.path.join('/home/mayankch283/carboncare-logistics-agent/uploads', 'uploaded_data.json')
        
        if not os.path.exists(json_file_path):
            app.logger.error(f"File not found: {json_file_path}")
            return jsonify({'error': 'No uploaded data found for training'}), 404
        
        with open(json_file_path, 'r') as json_file:
            historical_data = json.load(json_file)
        
        app.logger.info(f"Loaded data: {json.dumps(historical_data)[:200]}...")
        
        if not historical_data.get('data') or \
           not historical_data['data'].get('shipments') or \
           not historical_data['data'].get('sustainability_scores'):
            app.logger.error("Invalid data structure")
            return jsonify({
                'error': 'Missing required training data',
                'required_fields': ['data.shipments', 'data.sustainability_scores']
            }), 400
        
        shipments = historical_data['data']['shipments']
        sustainability_scores = historical_data['data']['sustainability_scores']

        if len(shipments) == 0:
            app.logger.error("No shipments found")
            return jsonify({'error': 'No historical data found for training'}), 404 
        
        app.logger.info(f"Training model with {len(shipments)} shipments")
        training_results = predictor.train(
            shipments,
            sustainability_scores
        )
        
        return jsonify({
            'message': 'Model trained successfully',
            'training_results': training_results
        }), 200
        
    except Exception as e:
        app.logger.error(f"Training error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/v1/sustainability/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple shipments in batch"""
    try:
        data = request.get_json()
        result = perform_batch_analysis(data)
        if isinstance(result, tuple):
            return result  # Error response
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
    
def perform_batch_analysis(data):
    """Perform batch analysis on shipments data"""
    if 'shipments' not in data:
        raise ValueError("Input data must contain 'shipments' key.")

    results = []
    for shipment in data['shipments']:
        analysis = analyze_sustainability(pipeline, shipment, predictor)
        llm_insights = get_llm_analysis(
            analysis['metrics'],
            analysis['overall_sustainability_score']
        )

        results.append({
            'shipment_id': shipment['shipment_id'],
            'sustainability_analysis': analysis,
            'llm_insights': llm_insights
        })

    return {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'num_shipments_analyzed': len(results),
        'results': results
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)