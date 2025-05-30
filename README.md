# Food Delivery Backend System

A microservices-based food delivery backend built with FastAPI, PostgreSQL, and Docker.

## 🚀 **Live Production URLs**

**🌐 Deployed Services:**
- **User Service**: https://food-delivery-user-service.onrender.com/docs
- **Restaurant Service**: https://food-delivery-restaurant-service.onrender.com/docs  
- **Delivery Agent Service**: https://food-delivery-delivery-service.onrender.com/docs

**🔗 Health Check Endpoints:**
- User Service Health: https://food-delivery-user-service.onrender.com/health
- Restaurant Service Health: https://food-delivery-restaurant-service.onrender.com/health
- Delivery Agent Service Health: https://food-delivery-delivery-service.onrender.com/health

## 🏗️ Architecture

The system consists of three microservices:

1. **User Service** (Port 8001)
   - User management and authentication
   - Restaurant listing and search
   - Order placement and tracking
   - Rating and review system

2. **Restaurant Service** (Port 8002)
   - Restaurant profile management
   - Menu and pricing management
   - Order processing and status updates
   - Automatic delivery agent assignment

3. **Delivery Agent Service** (Port 8003)
   - Delivery agent registration and management
   - Real-time delivery status updates
   - Route optimization and tracking

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger UI (auto-generated)
- **Deployment**: Render.com
- **Inter-service Communication**: HTTP/REST APIs

## 🚀 Quick Start (Local Development)

### Prerequisites
- Docker and Docker Compose installed
- Python 3.9+ (for local development)
- Git

### Using Docker (Recommended)

1. **Clone the repository**
\`\`\`bash
git clone https://github.com/yourusername/food-delivery-backend.git
cd food-delivery-backend
\`\`\`

2. **Start all services**
\`\`\`bash
docker-compose up --build
# OR run in background
docker-compose up -d
\`\`\`

3. **Access the services:**
   - User Service: http://localhost:8001/docs
   - Restaurant Service: http://localhost:8002/docs
   - Delivery Agent Service: http://localhost:8003/docs
   - PostgreSQL: localhost:5432

4. **Stop services**
\`\`\`bash
docker-compose down
\`\`\`

### Local Development (Without Docker)

1. **Install dependencies for each service:**
\`\`\`bash
# User Service
cd user_service
pip install -r requirements.txt

# Restaurant Service  
cd ../restaurant_service
pip install -r requirements.txt

# Delivery Agent Service
cd ../delivery_agent_service
pip install -r requirements.txt
\`\`\`

2. **Set up environment variables**
   - Copy `.env.example` to `.env` in each service directory
   - Update database connection strings

3. **Run each service in separate terminals:**
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

## 📋 API Endpoints

### User Service (Port 8001)
- `POST /users/` - Create new user
- `GET /users/{user_id}` - Get user details
- `PUT /users/{user_id}` - Update user information
- `GET /restaurants/available` - Get available restaurants
- `POST /orders/` - Place new order
- `GET /orders/user/{user_id}` - Get user's order history
- `PUT /orders/{order_id}/cancel` - Cancel order
- `POST /ratings/` - Submit rating and review

### Restaurant Service (Port 8002)
- `POST /restaurants/` - Create restaurant
- `GET /restaurants/{restaurant_id}` - Get restaurant details
- `PUT /restaurants/{restaurant_id}` - Update restaurant info
- `PUT /restaurants/{restaurant_id}/status` - Update online/offline status
- `POST /menu-items/restaurant/{restaurant_id}` - Add menu item
- `GET /menu-items/restaurant/{restaurant_id}` - Get restaurant menu
- `PUT /menu-items/{menu_item_id}` - Update menu item
- `GET /orders/restaurant/{restaurant_id}` - Get restaurant orders
- `PUT /orders/{order_id}/status` - Update order status

### Delivery Agent Service (Port 8003)
- `POST /agents/` - Register delivery agent
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}` - Update agent information
- `PUT /agents/{agent_id}/status` - Update availability status
- `GET /agents/available` - Get available agents
- `PUT /deliveries/{order_id}/status` - Update delivery status
- `GET /deliveries/agent/{agent_id}` - Get agent's deliveries

## 🗄️ Database Schema

The system uses PostgreSQL with the following tables:

### Core Tables
- **users** - User profiles and authentication
- **restaurants** - Restaurant information and status
- **menu_items** - Restaurant menu items and pricing
- **delivery_agents** - Delivery agent profiles
- **orders** - Order details and status
- **order_items** - Items within each order
- **ratings** - User ratings and reviews

### Key Relationships
- Users can place multiple orders
- Restaurants have multiple menu items
- Orders contain multiple order items
- Delivery agents can handle multiple deliveries
- Orders can have ratings from users

## 🧪 Testing

### Using Postman
1. **Import Collection**: Import `postman_collection.json`
2. **Set Environment Variables**:
   - `user_service_url`: `https://food-delivery-user-service.onrender.com`
   - `restaurant_service_url`: `https://food-delivery-restaurant-service.onrender.com`
   - `delivery_service_url`: `https://food-delivery-delivery-service.onrender.com`
3. **Test Endpoints**: Run the pre-configured requests

### Using Swagger UI
Visit the `/docs` endpoint for each service:
- User Service: https://food-delivery-user-service.onrender.com/docs
- Restaurant Service: https://food-delivery-restaurant-service.onrender.com/docs
- Delivery Agent Service: https://food-delivery-delivery-service.onrender.com/docs

### Sample Test Flow
1. **Create User** → **Create Restaurant** → **Add Menu Items**
2. **Create Delivery Agent** → **Place Order** → **Accept Order**
3. **Update Order Status** → **Update Delivery Status** → **Submit Rating**

## 🌐 Deployment (Render.com)

### Production Environment
- **Platform**: Render.com
- **Database**: PostgreSQL (500MB free tier)
- **Compute**: 750 hours/month free tier
- **Region**: Singapore (Asia-Pacific)

### Environment Variables
Each service uses these environment variables:
\`\`\`bash
DATABASE_URL=postgresql://postgres:password@host:port/food_delivery
SECRET_KEY=your-super-secret-key-here
USER_SERVICE_URL=https://food-delivery-user-service.onrender.com
RESTAURANT_SERVICE_URL=https://food-delivery-restaurant-service.onrender.com
DELIVERY_SERVICE_URL=https://food-delivery-delivery-service.onrender.com
\`\`\`

### Deployment Steps
1. **Database**: Create PostgreSQL database
2. **Services**: Deploy each microservice separately
3. **Environment**: Configure environment variables
4. **Testing**: Verify all endpoints work

## 🔧 Configuration

### Docker Configuration
- Each service has its own `Dockerfile`
- `docker-compose.yml` for local development
- Health checks implemented for all services

### Database Configuration
- Connection pooling enabled
- Automatic table creation on startup
- Sample data initialization
- Proper indexing for performance

## 🚨 Troubleshooting

### Common Issues

**Service Not Responding**
- Check if service is deployed and "Live" in Render dashboard
- Verify environment variables are set correctly
- Check service logs for errors

**Database Connection Issues**
- Verify DATABASE_URL format is correct
- Ensure database is in same region as services
- Check database connection limits

**Inter-service Communication Failures**
- Verify service URLs in environment variables
- Check if all services are deployed and accessible
- Test individual service health endpoints

### Render-Specific Notes
- **Cold Starts**: Free tier services sleep after 15 minutes of inactivity
- **Wake-up Time**: First request after sleep takes ~30 seconds
- **Build Time**: Initial deployment takes 10-20 minutes
- **Logs**: Check deployment logs in Render dashboard for errors

## 📊 Performance & Monitoring

### Performance Considerations
- Database connection pooling implemented
- Async HTTP requests for inter-service communication
- Proper error handling and timeouts
- Health check endpoints for monitoring

### Monitoring
- Health check endpoints: `/health`
- Service status monitoring via Render dashboard
- API documentation: `/docs` endpoints
- Database monitoring via Render PostgreSQL dashboard

## 🔒 Security Features

- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Proper HTTP status codes and error messages
- **CORS**: Configured for cross-origin requests
- **Environment Variables**: Sensitive data stored securely
- **Database**: PostgreSQL with proper constraints and indexes

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs` endpoints
- **Email**: [manasvigowda35@gmail.com]

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Powerful, open source object-relational database
- **Docker** - Containerization platform
- **Render** - Cloud platform for hosting

---

**🚀 Built with FastAPI, PostgreSQL, Docker, and deployed on Render.com**

**⭐ Star this repository if you found it helpful!**
