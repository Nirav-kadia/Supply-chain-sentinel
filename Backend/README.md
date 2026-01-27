# SupplyChain Sentinel Backend

FastAPI backend service for supply chain risk analysis.

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed
- `.env` file with required environment variables

### Environment Variables
Create a `.env` file with:
```
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password
GOOGLE_API_KEY=your_google_api_key
```

### Build and Run

#### Using Docker Compose (Recommended)
```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the service
docker-compose down
```

#### Using Docker directly
```bash
# Build the image
docker build -t supplychain-backend .

# Run the container
docker run -p 8000:8000 --env-file .env supplychain-backend
```

### Access
- API: http://localhost:8000
- Health check: http://localhost:8000/
- API docs: http://localhost:8000/docs

### Development
For development, you can mount the source code:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```