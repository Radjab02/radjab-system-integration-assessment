"""
Analytics API service
Sends merged data to Analytics API with retry logic
"""
import logging
import time
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import settings

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for sending data to Analytics API
    Implements retry logic with exponential backoff
    """
    
    def __init__(self):
        self.base_url = settings.ANALYTICS_API_BASE_URL
        self.endpoint = settings.ANALYTICS_API_ENDPOINT
        self.timeout = settings.ANALYTICS_API_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.backoff_base = settings.RETRY_BACKOFF_BASE
        self.backoff_multiplier = settings.RETRY_BACKOFF_MULTIPLIER
        
        # Create session with connection pooling
        self.session = self._create_session()
        
        logger.info(
            f"Analytics service initialized: "
            f"url={self.base_url}{self.endpoint}, "
            f"max_retries={self.max_retries}"
        )
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration"""
        session = requests.Session()
        
        # Configure retries for connection errors
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def send_analytics_data(self, payload: Dict[str, Any]) -> bool:
        """
        Send analytics data to API with retry logic
        
        Args:
            payload: Analytics data payload
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}{self.endpoint}"
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Sending analytics data to {url} "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                response.raise_for_status()
                
                result = response.json()
                logger.info(
                    f"Analytics data sent successfully: "
                    f"status={result.get('status')}, "
                    f"records={result.get('recordsProcessed')}"
                )
                
                return True
                
            except requests.exceptions.Timeout as e:
                logger.warning(
                    f"Timeout sending analytics data (attempt {attempt}): {e}"
                )
                if attempt < self.max_retries:
                    self._backoff(attempt)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(
                    f"HTTP error sending analytics data (attempt {attempt}): "
                    f"status={e.response.status_code}, error={e}"
                )
                
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Client error (4xx), not retrying: "
                        f"{e.response.text}"
                    )
                    return False
                
                if attempt < self.max_retries:
                    self._backoff(attempt)
                    
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Request error sending analytics data (attempt {attempt}): {e}"
                )
                if attempt < self.max_retries:
                    self._backoff(attempt)
            
            except Exception as e:
                logger.error(
                    f"Unexpected error sending analytics data (attempt {attempt}): {e}",
                    exc_info=True
                )
                if attempt < self.max_retries:
                    self._backoff(attempt)
        
        logger.error(
            f"Failed to send analytics data after {self.max_retries} attempts"
        )
        return False
    
    def _backoff(self, attempt: int) -> None:
        """
        Exponential backoff between retries
        
        Args:
            attempt: Current attempt number
        """
        delay = self.backoff_base * (self.backoff_multiplier ** (attempt - 1))
        logger.info(f"Backing off for {delay:.2f} seconds before retry...")
        time.sleep(delay)
    
    def health_check(self) -> bool:
        """
        Check if Analytics API is reachable
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Assuming there's a health endpoint
            health_url = f"{self.base_url}/actuator/health"
            response = self.session.get(health_url, timeout=5)
            
            if response.status_code == 200:
                logger.info("Analytics API is healthy")
                return True
            else:
                logger.warning(
                    f"Analytics API health check failed: "
                    f"status={response.status_code}"
                )
                return False
                
        except Exception as e:
            logger.warning(f"Analytics API health check error: {e}")
            return False
    
    def close(self) -> None:
        """Close the session"""
        self.session.close()
        logger.info("Analytics service session closed")
