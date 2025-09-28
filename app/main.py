from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database.connection import engine, get_db
from app.models.user import Base, User
from app.api.user_routes import router as user_router
from app.monitoring.metrics import PrometheusMetrics, CONTENT_TYPE_LATEST
from app.elasticsearch.client import es_client
from app.logging.logging import app_logger
import time
import socket
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Management API",
    description="A modular Python application for user CRUD operations with Prometheus monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for metrics collection and ELK logging
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request start
    app_logger.info(
        "Request started",
        method=request.method,
        endpoint=request.url.path,
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        PrometheusMetrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        # Log to Elasticsearch
        es_client.log_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
            ip_address=client_ip
        )
        
        # Log response
        app_logger.info(
            "Request completed",
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_ms=duration * 1000,
            client_ip=client_ip
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Log error to Elasticsearch
        es_client.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            request_id=getattr(request.state, 'request_id', None)
        )
        
        # Log error
        app_logger.error(
            "Request failed",
            method=request.method,
            endpoint=request.url.path,
            error=str(e),
            duration_ms=duration * 1000,
            client_ip=client_ip,
            exc_info=True
        )
        
        raise

# Include routers
app.include_router(user_router)

@app.get("/")
def root():
    return {
        "message": "User Management API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/v1/users",
            "metrics": "/metrics",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint including Elasticsearch status"""
    elasticsearch_healthy = es_client.health_check()
    
    health_status = {
        "status": "healthy" if elasticsearch_healthy else "degraded",
        "elasticsearch": "healthy" if elasticsearch_healthy else "unhealthy",
        "timestamp": time.time()
    }
    
    if not elasticsearch_healthy:
        app_logger.warning("Elasticsearch health check failed")
    
    return health_status

@app.get("/metrics")
def get_metrics():
    """Prometheus metrics endpoint"""
    # Update user metrics before serving
    db = next(get_db())
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    PrometheusMetrics.update_user_metrics(total_users, active_users)
    PrometheusMetrics.update_system_metrics()
    db.close()
    
    return Response(
        content=PrometheusMetrics.get_metrics(),
        media_type=CONTENT_TYPE_LATEST
    )

# OpenTelemetry Tracing Setup
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "user-mgt-pj"})
    )
)

otlp_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",  # Jaeger OTLP gRPC endpoint
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)