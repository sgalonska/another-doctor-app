"""HTTP client utilities with retry and error handling."""

import asyncio
from typing import Any, Dict, Optional, Union
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

class APIError(Exception):
    """API request error with status code and response data."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

class HTTPClient:
    """Async HTTP client with retry logic and structured logging."""
    
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        retry_attempts: int = 3,
        retry_backoff: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff
        
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "another-doctor/1.0",
        }
        if headers:
            default_headers.update(headers)
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=default_headers,
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        
        full_url = f"{self.base_url}{url}" if self.base_url and not url.startswith("http") else url
        
        logger.info(
            "http_request_start",
            method=method,
            url=full_url,
            params=params,
            has_json_body=json is not None,
        )
        
        try:
            response = await self.client.request(
                method=method,
                url=full_url,
                params=params,
                json=json,
                headers=headers,
                **kwargs,
            )
            
            logger.info(
                "http_request_complete",
                method=method,
                url=full_url,
                status_code=response.status_code,
                response_size=len(response.content),
            )
            
            if not response.is_success:
                error_data = {}
                try:
                    error_data = response.json()
                except Exception:
                    pass
                
                logger.error(
                    "http_request_failed",
                    method=method,
                    url=full_url,
                    status_code=response.status_code,
                    error_data=error_data,
                )
                
                raise APIError(
                    f"HTTP {response.status_code}: {response.reason_phrase}",
                    status_code=response.status_code,
                    response_data=error_data,
                )
            
            return response.json()
            
        except httpx.TimeoutException as e:
            logger.error(
                "http_request_timeout",
                method=method,
                url=full_url,
                error=str(e),
            )
            raise APIError(f"Request timeout: {url}") from e
        
        except httpx.RequestError as e:
            logger.error(
                "http_request_error",
                method=method,
                url=full_url,
                error=str(e),
            )
            raise APIError(f"Request failed: {url}") from e
    
    async def get(
        self, 
        url: str, 
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make GET request."""
        return await self.request("GET", url, params=params, **kwargs)
    
    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make POST request."""
        return await self.request("POST", url, json=json, **kwargs)
    
    async def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return await self.request("PUT", url, json=json, **kwargs)
    
    async def delete(
        self,
        url: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self.request("DELETE", url, **kwargs)