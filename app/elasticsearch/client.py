from elasticsearch import Elasticsearch
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from app.logging.logging import app_logger

class ElasticsearchClient:
    def __init__(self, host: str = "localhost", port: int = 9200):
        """Initialize Elasticsearch client"""
        self.client = Elasticsearch([f"http://{host}:{port}"])
        self.index_prefix = "user-mgt"
        
    def health_check(self) -> bool:
        """Check Elasticsearch cluster health"""
        try:
            health = self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
        except Exception as e:
            app_logger.error("Elasticsearch health check failed", error=str(e))
            return False
    
    def create_index(self, index_name: str, mapping: Dict[str, Any] = None) -> bool:
        """Create an index with optional mapping"""
        try:
            if not self.client.indices.exists(index=index_name):
                body = {}
                if mapping:
                    body["mappings"] = mapping
                self.client.indices.create(index=index_name, body=body)
                app_logger.info("Index created", index=index_name)
                return True
            return True
        except Exception as e:
            app_logger.error("Failed to create index", index=index_name, error=str(e))
            return False
    
    def index_document(self, index_name: str, document: Dict[str, Any], doc_id: str = None) -> bool:
        """Index a document"""
        try:
            result = self.client.index(
                index=index_name,
                body=document,
                id=doc_id
            )
            app_logger.debug("Document indexed", index=index_name, doc_id=result['_id'])
            return True
        except Exception as e:
            app_logger.error("Failed to index document", index=index_name, error=str(e))
            return False
    
    def search_documents(self, index_name: str, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        """Search documents in an index"""
        try:
            result = self.client.search(
                index=index_name,
                body=query,
                size=size
            )
            return [hit['_source'] for hit in result['hits']['hits']]
        except Exception as e:
            app_logger.error("Search failed", index=index_name, error=str(e))
            return []
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None):
        """Log user actions to Elasticsearch"""
        index_name = f"{self.index_prefix}-user-actions-{datetime.now().strftime('%Y.%m.%d')}"
        
        document = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "service": "user-mgt-api",
            "environment": "development",
            "details": details or {}
        }
        
        return self.index_document(index_name, document)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       duration: float, user_id: int = None, ip_address: str = None):
        """Log API requests to Elasticsearch"""
        index_name = f"{self.index_prefix}-api-requests-{datetime.now().strftime('%Y.%m.%d')}"
        
        document = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "user_id": user_id,
            "ip_address": ip_address,
            "service": "user-mgt-api",
            "environment": "development"
        }
        
        return self.index_document(index_name, document)
    
    def log_error(self, error_type: str, error_message: str, stack_trace: str = None, 
                  user_id: int = None, request_id: str = None):
        """Log errors to Elasticsearch"""
        index_name = f"{self.index_prefix}-errors-{datetime.now().strftime('%Y.%m.%d')}"
        
        document = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "user_id": user_id,
            "request_id": request_id,
            "service": "user-mgt-api",
            "environment": "development"
        }
        
        return self.index_document(index_name, document)

# Global Elasticsearch client instance
es_client = ElasticsearchClient()
