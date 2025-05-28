-- Create database schema for food delivery system

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    cuisine_type VARCHAR(50),
    is_online BOOLEAN DEFAULT true,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu items table
CREATE TABLE IF NOT EXISTS menu_items (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    is_available BOOLEAN DEFAULT true,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery agents table
CREATE TABLE IF NOT EXISTS delivery_agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50),
    is_available BOOLEAN DEFAULT true,
    current_location TEXT,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    delivery_agent_id INTEGER REFERENCES delivery_agents(id),
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    delivery_address TEXT NOT NULL,
    special_instructions TEXT,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_delivery_time TIMESTAMP,
    actual_delivery_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    special_requests TEXT
);

-- Ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    delivery_agent_id INTEGER REFERENCES delivery_agents(id),
    restaurant_rating INTEGER CHECK (restaurant_rating >= 1 AND restaurant_rating <= 5),
    delivery_rating INTEGER CHECK (delivery_rating >= 1 AND delivery_rating <= 5),
    restaurant_review TEXT,
    delivery_review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_restaurants_is_online ON restaurants(is_online);
CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant_id ON menu_items(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_menu_items_is_available ON menu_items(is_available);
CREATE INDEX IF NOT EXISTS idx_delivery_agents_is_available ON delivery_agents(is_available);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_orders_delivery_agent_id ON orders(delivery_agent_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_ratings_order_id ON ratings(order_id);

-- Insert sample data
INSERT INTO users (name, email, phone, address) VALUES
('John Doe', 'john@example.com', '+1234567890', '123 Main St, City, State'),
('Jane Smith', 'jane@example.com', '+1234567891', '456 Oak Ave, City, State'),
('Bob Johnson', 'bob@example.com', '+1234567892', '789 Pine Rd, City, State');

INSERT INTO restaurants (name, description, address, phone, email, cuisine_type, is_online) VALUES
('Pizza Palace', 'Best pizza in town', '100 Food St, City, State', '+1234567800', 'info@pizzapalace.com', 'Italian', true),
('Burger Barn', 'Gourmet burgers and fries', '200 Taste Ave, City, State', '+1234567801', 'info@burgerbarn.com', 'American', true),
('Sushi Spot', 'Fresh sushi and Japanese cuisine', '300 Fresh Blvd, City, State', '+1234567802', 'info@sushispot.com', 'Japanese', false);

INSERT INTO menu_items (restaurant_id, name, description, price, category, is_available) VALUES
(1, 'Margherita Pizza', 'Classic pizza with tomato, mozzarella, and basil', 12.99, 'Pizza', true),
(1, 'Pepperoni Pizza', 'Pizza with pepperoni and mozzarella', 14.99, 'Pizza', true),
(1, 'Caesar Salad', 'Fresh romaine lettuce with caesar dressing', 8.99, 'Salad', true),
(2, 'Classic Burger', 'Beef patty with lettuce, tomato, and onion', 10.99, 'Burger', true),
(2, 'Cheese Fries', 'Crispy fries with melted cheese', 6.99, 'Sides', true),
(2, 'Chocolate Shake', 'Rich chocolate milkshake', 4.99, 'Beverages', true),
(3, 'California Roll', 'Crab, avocado, and cucumber roll', 8.99, 'Sushi', true),
(3, 'Salmon Nigiri', 'Fresh salmon over seasoned rice', 12.99, 'Sushi', true);

INSERT INTO delivery_agents (name, email, phone, vehicle_type, is_available) VALUES
('Mike Wilson', 'mike@delivery.com', '+1234567900', 'Motorcycle', true),
('Sarah Davis', 'sarah@delivery.com', '+1234567901', 'Car', true),
('Tom Brown', 'tom@delivery.com', '+1234567902', 'Bicycle', false);
