#!/bin/bash

# Quick Start Script for Systems Integration Assignment
# Task 1: Mock API Setup

set -e

echo "=========================================="
echo "Systems Integration Assignment"
echo "Quick Start - Task 1: Mock APIs"
echo "=========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose detected"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Services Started Successfully!"
echo "=========================================="
echo ""
echo "📊 Access Points:"
echo "  - Mock APIs (Swagger): http://localhost:8081/swagger-ui.html"
echo "  - Kafka UI:            http://localhost:8090"
echo "  - H2 Console:          http://localhost:8081/h2-console"
echo ""
echo "🧪 Test Commands:"
echo "  # Get customers"
echo "  curl http://localhost:8081/api/customers"
echo ""
echo "  # Get products"
echo "  curl http://localhost:8081/api/products"
echo ""
echo "  # Get WSDL"
echo "  curl http://localhost:8081/ws/customers?wsdl"
echo ""
echo "📝 View logs:"
echo "  docker-compose logs -f mock-apis"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose down"
echo ""
echo "=========================================="
