# Food Delivery Backend System

A microservices-based food delivery backend built with FastAPI, PostgreSQL, and Docker.

## Architecture

The system consists of three microservices:

1. **User Service** (Port 8001)
   - User management
   - Restaurant listing
   - Order placement
   - Rating system

2. **Restaurant Service** (Port 8002)
   - Restaurant management
   - Menu management
   - Order processing
   - Delivery agent assignment

3. **Delivery Agent Service** (Port 8003)
   - Delivery agent management
   - Order delivery status updates

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger UI (auto-generated)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.9+ (for local development)

### Using Docker (Recommended)

1. Clone the repository
\`\`\`bash
git clone <repository-url>
cd food-delivery-backend
\`\`\`

2. Start all services
\`\`\`bash
docker-compose up --build
\`\`\`

3. Access the services:
   - User Service: http://localhost:8001/docs
   - Restaurant Service: http://localhost:8002/docs
   - Delivery Agent Service: http://localhost:8003/docs
   - PostgreSQL: localhost:5432

### Local Development

1. Install dependencies for each service:
\`\`\`bash
# For each service directory
pip install -r requirements.txt
\`\`\`

2. Set up environment variables (copy .env.example to .env in each service)

3. Run each service:
\`\`\`bash
# Terminal 1 - User Service
cd user_service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Restaurant Service
cd restaurant_service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 3 - Delivery Agent Service
cd delivery_agent_service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
\`\`\`

## API Endpoints

### User Service (Port 8001)
- `POST /users/` - Create user
- `GET /users/{user_id}` - Get user details
- `GET /restaurants/available` - Get available restaurants
- `POST /orders/` - Place order
- `GET /orders/user/{user_id}` - Get user orders
- `POST /ratings/` - Submit rating

### Restaurant Service (Port 8002)
- `POST /restaurants/` - Create restaurant
- `GET /restaurants/{restaurant_id}` - Get restaurant details
- `PUT /restaurants/{restaurant_id}/status` - Update restaurant status
- `POST /restaurants/{restaurant_id}/menu` - Add menu item
- `GET /restaurants/{restaurant_id}/menu` - Get menu
- `PUT /orders/{order_id}/status` - Update order status
- `GET /orders/restaurant/{restaurant_id}` - Get restaurant orders

### Delivery Agent Service (Port 8003)
- `POST /agents/` - Create delivery agent
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}/status` - Update agent availability
- `PUT /deliveries/{order_id}/status` - Update delivery status
- `GET /deliveries/agent/{agent_id}` - Get agent deliveries

## Database Schema

The system uses PostgreSQL with the following main tables:
- users
- restaurants
- menu_items
- delivery_agents
- orders
- order_items
- ratings

## Testing

Import the Postman collection from `postman_collection.json` to test all endpoints.

## Deployment

The application is containerized and can be deployed on:
- Heroku (using heroku.yml)
- AWS ECS
- Google Cloud Run
- Any Docker-compatible platform

## Environment Variables

Each service requires the following environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- Service-specific configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
