#!/bin/bash

# ELK Stack Startup Script for User Management API

echo "🚀 Starting ELK Stack for User Management API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start ELK stack
echo "📦 Starting ELK stack containers..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check Elasticsearch health
echo "🔍 Checking Elasticsearch health..."
until curl -s http://localhost:9200/_cluster/health > /dev/null; do
    echo "   Waiting for Elasticsearch..."
    sleep 5
done

echo "✅ Elasticsearch is ready!"

# Check Kibana
echo "🔍 Checking Kibana..."
until curl -s http://localhost:5601 > /dev/null; do
    echo "   Waiting for Kibana..."
    sleep 5
done

echo "✅ Kibana is ready!"

# Check Logstash
echo "🔍 Checking Logstash..."
until curl -s http://localhost:9600/_node/stats > /dev/null; do
    echo "   Waiting for Logstash..."
    sleep 5
done

echo "✅ Logstash is ready!"

echo ""
echo "🎉 ELK Stack is running successfully!"
echo ""
echo "📊 Access URLs:"
echo "   Elasticsearch: http://localhost:9200"
echo "   Kibana:        http://localhost:5601"
echo "   Logstash:      http://localhost:9600"
echo ""
echo "🚀 You can now start your application with:"
echo "   python run.py"
echo ""
echo "📝 To stop the ELK stack, run:"
echo "   docker compose down"
