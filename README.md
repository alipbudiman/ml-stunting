# ML Stunting FastAPI Template
---
Note: maaf berantakan, kalo sempat nanti di rapihkan


Simple and clean FastAPI template for ML Stunting prediction service.

## Features

- ✅ Health check endpoints
- ✅ Prediction endpoint with Pydantic models
- ✅ Error handling
- ✅ API documentation (auto-generated)
- ✅ Clean project structure

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the development server:
```bash
python main.py
```

2. Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Health check (root endpoint)
- `GET /health` - Health check endpoint
- `POST /predict` - Prediction endpoint
- `GET /model/info` - Get model information
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Make Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "feature1": 0.8,
       "feature2": 0.6,
       "feature3": 0.4
     }'
```

## Project Structure

```
sourceml/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── model_*.pkl         # Your ML models
└── encoders.pkl        # Your encoders
```

## Next Steps

1. Replace the dummy prediction logic in `main.py` with your actual ML model
2. Load your saved models (`model_bbtb.pkl`, `model_bbu.pkl`, `model_tbu.pkl`)
3. Update the `PredictionRequest` model with your actual features
4. Add more endpoints as needed
5. Add authentication if required
6. Add logging and monitoring

## Notes

- The template includes basic error handling
- Pydantic models ensure request/response validation
- FastAPI automatically generates OpenAPI documentation
- The server runs with auto-reload for development
