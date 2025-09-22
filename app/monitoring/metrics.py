from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Total number of active users'
)

TOTAL_USERS = Gauge(
    'users_total',
    'Total number of users'
)

class PrometheusMetrics:
    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    @staticmethod
    def update_user_metrics(total_users: int, active_users: int):
        """Update user-related metrics"""
        TOTAL_USERS.set(total_users)
        ACTIVE_USERS.set(active_users)

    @staticmethod
    def get_metrics():
        """Get metrics in Prometheus format"""
        return generate_latest()