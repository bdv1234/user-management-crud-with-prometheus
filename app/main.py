from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database.connection import engine, get_db
from app.models.user import Base, User
from app.api.user_routes import router as user_router
from app.monitoring.metrics import PrometheusMetrics, CONTENT_TYPE_LATEST
import time
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

# Middleware for metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    PrometheusMetrics.record_request(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration
    )
    
    return response

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
    return {"status": "healthy"}

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