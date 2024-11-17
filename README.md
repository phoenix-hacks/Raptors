# CarbonCare - Sustainability Intelligence Platform 🌱

CarbonCare is an AI-powered platform that helps logistics businesses optimize their operations for sustainability. Through advanced analytics and machine learning, it provides actionable insights to reduce carbon footprint, improve resource efficiency, and make supply chains more environmentally friendly.

![CarbonCare Dashboard](https://github.com/user-attachments/assets/cd64a290-373d-4709-83f9-9cfdb1899bb9)


## ✨ Key Features

- **Real-time Sustainability Analytics**: Monitor key metrics like carbon emissions, resource utilization, and energy efficiency
- **AI-powered Insights**: Get actionable recommendations from our ML model to improve sustainability scores
- **Interactive Dashboard**: Visualize sustainability data through intuitive charts and metrics
- **Predictive Analytics**: Forecast environmental impact and optimize future shipments
- **Batch Analysis**: Process multiple shipments to identify patterns and optimization opportunities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 15+
- React 18+
- PostgreSQL with Supabase

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/carboncare.git

# Enter server directory
cd carboncare/server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start server
python [app.py](http://_vscodecontentref_/0)
```
### Frontend Setup
```
# Enter client directory
cd ../client

# Install dependencies
npm install

# Start development server
npm run dev
```
## 🏗️ Architecture
Frontend: Next.js, Tailwind CSS, Recharts
Backend: Flask, scikit-learn, LangChain
Database: PostgreSQL (Supabase)
ML Model: Random Forest for sustainability prediction
API: RESTful endpoints with JWT authentication

## 📊 Core Metrics
The platform analyzes several key sustainability metrics:

Package Sustainability Index (PSI) <br>
Route Efficiency Score (RES) <br>
Carbon Emission Index (CEI) <br>
Resource Utilization Rate (RUR) <br>
Energy Efficiency Rating (EER) <br>
Waste Reduction Score (WRS) <br>

## 🔒 Security
JWT-based authentication
Role-based access control
Secure API endpoints
Environment variable protection
