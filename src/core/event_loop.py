"""
Event loop management with uvloop fallback support.

This module provides intelligent event loop selection with automatic fallback
to the standard asyncio event loop if uvloop is not available or compatible.
"""

import asyncio
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)


class EventLoopManager:
    """Manages event loop selection with uvloop fallback."""
    
    _loop_policy: Optional[asyncio.AbstractEventLoopPolicy] = None
    _uvloop_available: Optional[bool] = None
    
    @classmethod
    def is_uvloop_available(cls) -> bool:
        """Check if uvloop is available and compatible."""
        if cls._uvloop_available is not None:
            return cls._uvloop_available
        
        try:
            # Only try uvloop on non-Windows platforms
            if sys.platform == 'win32':
                cls._uvloop_available = False
                return False
            
            import uvloop
            
            # Test if uvloop can create a policy (compatibility check)
            test_policy = uvloop.EventLoopPolicy()
            cls._uvloop_available = True
            logger.info("uvloop is available and compatible")
            return True
            
        except ImportError:
            logger.info("uvloop not installed, using standard asyncio")
            cls._uvloop_available = False
            return False
        except Exception as e:
            logger.warning(f"uvloop available but incompatible: {e}")
            cls._uvloop_available = False
            return False
    
    @classmethod
    def setup_event_loop(cls, force_asyncio: bool = False) -> str:
        """
        Setup the optimal event loop policy.
        
        Args:
            force_asyncio: If True, force use of standard asyncio
            
        Returns:
            String indicating which event loop was selected
        """
        if force_asyncio:
            logger.info("Forcing standard asyncio event loop")
            return "asyncio"
        
        if cls.is_uvloop_available():
            try:
                import uvloop
                uvloop.install()
                cls._loop_policy = uvloop.EventLoopPolicy()
                logger.info("✅ Using uvloop for enhanced async performance")
                return "uvloop"
            except Exception as e:
                logger.warning(f"Failed to install uvloop: {e}, falling back to asyncio")
        
        # Fallback to standard asyncio
        logger.info("Using standard asyncio event loop")
        return "asyncio"
    
    @classmethod
    def get_event_loop_info(cls) -> dict:
        """Get information about the current event loop."""
        try:
            loop = asyncio.get_running_loop()
            loop_type = type(loop).__name__
            
            # Determine if uvloop is being used
            is_uvloop = "uvloop" in loop_type.lower()
            
            return {
                "loop_type": loop_type,
                "is_uvloop": is_uvloop,
                "is_running": True,
                "uvloop_available": cls.is_uvloop_available(),
                "platform": sys.platform,
            }
        except RuntimeError:
            return {
                "loop_type": "None",
                "is_uvloop": False,
                "is_running": False,
                "uvloop_available": cls.is_uvloop_available(),
                "platform": sys.platform,
            }
    
    @classmethod
    def create_optimized_loop(cls) -> asyncio.AbstractEventLoop:
        """Create an optimized event loop."""
        if cls.is_uvloop_available():
            try:
                import uvloop
                return uvloop.new_event_loop()
            except Exception as e:
                logger.warning(f"Failed to create uvloop: {e}")
        
        return asyncio.new_event_loop()


def setup_async_environment(force_asyncio: bool = False) -> dict:
    """
    Setup the async environment with optimal event loop.
    
    Args:
        force_asyncio: Force use of standard asyncio
        
    Returns:
        Dictionary with setup information
    """
    loop_type = EventLoopManager.setup_event_loop(force_asyncio)
    loop_info = EventLoopManager.get_event_loop_info()
    
    return {
        "selected_loop": loop_type,
        "loop_info": loop_info,
        "performance_optimized": loop_type == "uvloop",
    }


def get_async_performance_info() -> dict:
    """Get detailed async performance information."""
    return {
        "event_loop": EventLoopManager.get_event_loop_info(),
        "uvloop_available": EventLoopManager.is_uvloop_available(),
        "platform_support": sys.platform != 'win32',
        "recommendations": _get_performance_recommendations(),
    }


def _get_performance_recommendations() -> list:
    """Get performance recommendations based on current setup."""
    recommendations = []
    
    if not EventLoopManager.is_uvloop_available():
        if sys.platform != 'win32':
            recommendations.append(
                "Install uvloop for better async performance: poetry install --extras performance"
            )
        else:
            recommendations.append(
                "uvloop is not supported on Windows, using standard asyncio"
            )
    
    loop_info = EventLoopManager.get_event_loop_info()
    if loop_info["is_running"] and not loop_info["is_uvloop"]:
        recommendations.append(
            "Consider using uvloop for enhanced async performance"
        )
    
    return recommendations
