# Deployment Guide

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- PostgreSQL (if running locally without Docker)

### Quick Start with Docker
1. Clone the repository
2. Run `docker-compose up --build`
3. Services will be available at:
   - User Service: http://localhost:8001
   - Restaurant Service: http://localhost:8002
   - Delivery Agent Service: http://localhost:8003

## Heroku Deployment

### Method 1: Using Heroku CLI

1. Install Heroku CLI
2. Login to Heroku: `heroku login`
3. Create three apps:
   \`\`\`bash
   heroku create your-app-user-service
   heroku create your-app-restaurant-service
   heroku create your-app-delivery-service
   \`\`\`

4. Add PostgreSQL addon to each app:
   \`\`\`bash
   heroku addons:create heroku-postgresql:mini -a your-app-user-service
   heroku addons:create heroku-postgresql:mini -a your-app-restaurant-service
   heroku addons:create heroku-postgresql:mini -a your-app-delivery-service
   \`\`\`

5. Set environment variables for each app:
   \`\`\`bash
   # User Service
   heroku config:set SECRET_KEY=your-secret-key -a your-app-user-service
   heroku config:set RESTAURANT_SERVICE_URL=https://your-app-restaurant-service.herokuapp.com -a your-app-user-service
   heroku config:set DELIVERY_SERVICE_URL=https://your-app-delivery-service.herokuapp.com -a your-app-user-service
   
   # Restaurant Service
   heroku config:set SECRET_KEY=your-secret-key -a your-app-restaurant-service
   heroku config:set USER_SERVICE_URL=https://your-app-user-service.herokuapp.com -a your-app-restaurant-service
   heroku config:set DELIVERY_SERVICE_URL=https://your-app-delivery-service.herokuapp.com -a your-app-restaurant-service
   
   # Delivery Service
   heroku config:set SECRET_KEY=your-secret-key -a your-app-delivery-service
   heroku config:set USER_SERVICE_URL=https://your-app-user-service.herokuapp.com -a your-app-delivery-service
   heroku config:set RESTAURANT_SERVICE_URL=https://your-app-restaurant-service.herokuapp.com -a your-app-delivery-service
   \`\`\`

6. Deploy each service:
   \`\`\`bash
   # Deploy User Service
   cd user_service
   git init
   heroku git:remote -a your-app-user-service
   git add .
   git commit -m "Deploy user service"
   git push heroku main
   
   # Deploy Restaurant Service
   cd ../restaurant_service
   git init
   heroku git:remote -a your-app-restaurant-service
   git add .
   git commit -m "Deploy restaurant service"
   git push heroku main
   
   # Deploy Delivery Service
   cd ../delivery_agent_service
   git init
   heroku git:remote -a your-app-delivery-service
   git add .
   git commit -m "Deploy delivery service"
   git push heroku main
   \`\`\`

### Method 2: Using Container Registry

1. Build and push Docker images:
   \`\`\`bash
   # User Service
   heroku container:push web -a your-app-user-service --context-path=./user_service
   heroku container:release web -a your-app-user-service
   
   # Restaurant Service
   heroku container:push web -a your-app-restaurant-service --context-path=./restaurant_service
   heroku container:release web -a your-app-restaurant-service
   
   # Delivery Service
   heroku container:push web -a your-app-delivery-service --context-path=./delivery_agent_service
   heroku container:release web -a your-app-delivery-service
   \`\`\`

## AWS ECS Deployment

### Prerequisites
- AWS CLI configured
- Docker images pushed to ECR

### Steps
1. Create ECS cluster
2. Create task definitions for each service
3. Create services in the cluster
4. Set up Application Load Balancer
5. Configure environment variables

## Google Cloud Run Deployment

### Steps
1. Build and push images to Google Container Registry
2. Deploy each service to Cloud Run
3. Set up environment variables
4. Configure service-to-service communication

## Environment Variables

Each service requires these environment variables:

### Common Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key

### Service-Specific Variables
- `USER_SERVICE_URL`: URL of user service
- `RESTAURANT_SERVICE_URL`: URL of restaurant service
- `DELIVERY_SERVICE_URL`: URL of delivery service

## Database Migration

Run this SQL script to initialize the database:
\`\`\`sql
-- See init.sql file for complete schema
\`\`\`

## Health Checks

Each service provides health check endpoints:
- `/health` - Basic health check
- `/docs` - Swagger documentation

## Monitoring and Logging

- Use application logs for debugging
- Monitor API response times
- Set up alerts for service failures
- Use database connection pooling for better performance

## Security Considerations

- Use HTTPS in production
- Implement proper authentication
- Validate all input data
- Use environment variables for secrets
- Implement rate limiting
- Use CORS properly

## Scaling

- Each service can be scaled independently
- Use load balancers for high availability
- Consider using Redis for caching
- Implement database read replicas for better performance
