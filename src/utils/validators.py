import re
import base64
import json
from typing import Dict, Optional, Tuple
import aiohttp
import asyncio

try:
    # Try relative imports first (for package execution)
    from ..core.exceptions import ValidationError
    from ..core.interfaces import ITokenValidator
    from ..core.types import TokenInfo
    from ..config.logging import StructuredLogger
except ImportError:
    # Fall back to absolute imports (for direct execution via run_bot.py)
    from core.exceptions import ValidationError
    from core.interfaces import ITokenValidator
    from core.types import TokenInfo
    from config.logging import StructuredLogger


class TokenValidator(ITokenValidator):
    
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self.logger = StructuredLogger("utils.token_validator")
        
        # Discord API endpoints
        self.api_base = "https://discord.com/api/v10"
        self.user_endpoint = f"{self.api_base}/users/@me"
        
        # Token format patterns
        self.token_patterns = [
            # Bot token pattern
            re.compile(r'^[A-Za-z0-9_-]{23,28}\.[A-Za-z0-9_-]{6,7}\.[A-Za-z0-9_-]{27,}$'),
            # User token pattern (older format)
            re.compile(r'^[A-Za-z0-9_-]{59,}$'),
            # User token pattern (newer format)
            re.compile(r'^mfa\.[A-Za-z0-9_-]{84,}$'),
        ]
    
    async def validate_format(self, token: str) -> bool:
        if not token or not isinstance(token, str):
            return False
        
        # Remove any whitespace
        token = token.strip()
        
        # Check minimum length
        if len(token) < 50:
            return False
        
        # Check against known patterns
        for pattern in self.token_patterns:
            if pattern.match(token):
                self.logger.debug("Token format validation passed")
                return True
        
        self.logger.debug("Token format validation failed")
        return False
    
    async def validate_api(self, token: str) -> bool:
        try:
            # First check format
            if not await self.validate_format(token):
                return False
            
            # Make API request
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (https://github.com/discord-selfbot, 1.0.0)"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(self.user_endpoint, headers=headers) as response:
                    if response.status == 200:
                        self.logger.debug("Token API validation passed")
                        return True
                    elif response.status == 401:
                        self.logger.debug("Token API validation failed: Unauthorized")
                        return False
                    else:
                        self.logger.warning(f"Token API validation failed: HTTP {response.status}")
                        return False
        
        except asyncio.TimeoutError:
            self.logger.warning("Token API validation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Token API validation error: {e}")
            return False
    
    async def extract_info(self, token: str) -> Dict[str, any]:
        info = {
            "token_valid": False,
            "format_valid": False,
            "api_valid": False,
            "user_id": None,
            "username": None,
            "discriminator": None,
            "verified": None,
            "mfa_enabled": None,
            "email": None,
            "phone": None,
            "error": None
        }
        
        try:
            # Validate format
            info["format_valid"] = await self.validate_format(token)
            if not info["format_valid"]:
                info["error"] = "Invalid token format"
                return info
            
            # Extract user ID from token if possible
            user_id = self._extract_user_id_from_token(token)
            if user_id:
                info["user_id"] = user_id
            
            # Validate with API and get user info
            user_data = await self._get_user_data(token)
            if user_data:
                info["api_valid"] = True
                info["token_valid"] = True
                
                # Extract user information
                info.update({
                    "user_id": str(user_data.get("id", "")),
                    "username": user_data.get("username", ""),
                    "discriminator": user_data.get("discriminator", ""),
                    "verified": user_data.get("verified", False),
                    "mfa_enabled": user_data.get("mfa_enabled", False),
                    "email": user_data.get("email"),
                    "phone": user_data.get("phone"),
                })
            else:
                info["error"] = "Token is invalid or expired"
        
        except Exception as e:
            info["error"] = str(e)
            self.logger.error(f"Error extracting token info: {e}")
        
        return info
    
    async def create_token_info(self, token: str) -> TokenInfo:
        info = await self.extract_info(token)
        
        return TokenInfo(
            token=token,  # Will be masked in __post_init__
            is_valid=info["token_valid"],
            user_id=info["user_id"],
            username=info["username"],
            discriminator=info["discriminator"],
            verified=info["verified"],
            mfa_enabled=info["mfa_enabled"],
            error_message=info["error"]
        )
    
    def _extract_user_id_from_token(self, token: str) -> Optional[str]:
        try:
            # For bot tokens, the user ID is in the first part
            if '.' in token:
                parts = token.split('.')
                if len(parts) >= 1:
                    # Decode base64 user ID
                    user_id_b64 = parts[0]
                    # Add padding if needed
                    padding = 4 - (len(user_id_b64) % 4)
                    if padding != 4:
                        user_id_b64 += '=' * padding
                    
                    try:
                        user_id_bytes = base64.b64decode(user_id_b64)
                        user_id = user_id_bytes.decode('utf-8')
                        return user_id
                    except Exception:
                        pass
        
        except Exception:
            pass
        
        return None
    
    async def _get_user_data(self, token: str) -> Optional[Dict[str, any]]:
        try:
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (https://github.com/discord-selfbot, 1.0.0)"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(self.user_endpoint, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        
        except Exception as e:
            self.logger.error(f"Error getting user data: {e}")
            return None


# Convenience functions for quick validation
async def validate_token_format(token: str) -> bool:
    validator = TokenValidator()
    return await validator.validate_format(token)


async def validate_token_api(token: str, timeout: float = 10.0) -> bool:
    validator = TokenValidator(timeout=timeout)
    return await validator.validate_api(token)


async def get_token_info(token: str, timeout: float = 10.0) -> TokenInfo:
    validator = TokenValidator(timeout=timeout)
    return await validator.create_token_info(token)


async def main() -> None:
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.utils.validators <token> [password]")
        sys.exit(1)
    
    token = sys.argv[1]
    
    print("🔍 Validating Discord token...")
    print("=" * 50)
    
    try:
        # Create validator
        validator = TokenValidator()
        
        # Get comprehensive info
        info = await validator.extract_info(token)
        
        # Display results
        print(f"Format Valid: {'✅' if info['format_valid'] else '❌'}")
        print(f"API Valid: {'✅' if info['api_valid'] else '❌'}")
        print(f"Overall Valid: {'✅' if info['token_valid'] else '❌'}")
        
        if info['user_id']:
            print(f"User ID: {info['user_id']}")
        if info['username']:
            print(f"Username: {info['username']}#{info['discriminator']}")
        if info['verified'] is not None:
            print(f"Verified: {'✅' if info['verified'] else '❌'}")
        if info['mfa_enabled'] is not None:
            print(f"MFA Enabled: {'✅' if info['mfa_enabled'] else '❌'}")
        
        if info['error']:
            print(f"Error: {info['error']}")
    
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
