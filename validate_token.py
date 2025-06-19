#!/usr/bin/env python3
"""
Standalone Discord token validator utility.

This script validates Discord tokens without importing the full bot framework,
avoiding circular import issues.
"""

import asyncio
import base64
import json
import re
import sys
from typing import Dict, Any, Optional

import aiohttp


class TokenValidator:
    """Standalone Discord token validator."""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def validate_format(self, token: str) -> bool:
        """Validate Discord token format."""
        if not token or not isinstance(token, str):
            return False
        
        # Discord token pattern: base64.base64.base64
        pattern = r'^[A-Za-z0-9_-]{23,28}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,}$'
        return bool(re.match(pattern, token))
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """Extract user ID from Discord token."""
        if not self.validate_format(token):
            return None
        
        try:
            # First part of token contains base64-encoded user ID
            user_id_part = token.split('.')[0]
            # Add padding if needed
            padding = 4 - (len(user_id_part) % 4)
            if padding != 4:
                user_id_part += '=' * padding
            
            decoded = base64.b64decode(user_id_part)
            return decoded.decode('utf-8')
        except Exception:
            return None
    
    async def validate_api(self, token: str) -> Dict[str, Any]:
        """Validate token against Discord API."""
        if not self.session:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                return await self._make_api_request(session, token)
        else:
            return await self._make_api_request(self.session, token)
    
    async def _make_api_request(self, session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
        """Make API request to validate token."""
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'DiscordBot (https://github.com/example/bot, 1.0.0)'
        }
        
        try:
            async with session.get('https://discord.com/api/v10/users/@me', headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'valid': True,
                        'user_data': data,
                        'status_code': response.status,
                        'error': None
                    }
                else:
                    error_text = await response.text()
                    return {
                        'valid': False,
                        'user_data': None,
                        'status_code': response.status,
                        'error': f"HTTP {response.status}: {error_text}"
                    }
        except asyncio.TimeoutError:
            return {
                'valid': False,
                'user_data': None,
                'status_code': None,
                'error': "Request timeout"
            }
        except Exception as e:
            return {
                'valid': False,
                'user_data': None,
                'status_code': None,
                'error': str(e)
            }
    
    async def validate_comprehensive(self, token: str) -> Dict[str, Any]:
        """Perform comprehensive token validation."""
        result = {
            'token': token[:10] + "..." if len(token) > 10 else token,
            'format_valid': False,
            'api_valid': False,
            'user_id': None,
            'user_data': None,
            'error': None
        }
        
        # Check format
        result['format_valid'] = self.validate_format(token)
        if not result['format_valid']:
            result['error'] = "Invalid token format"
            return result
        
        # Extract user ID
        result['user_id'] = self.extract_user_id(token)
        
        # Check API
        api_result = await self.validate_api(token)
        result['api_valid'] = api_result['valid']
        result['user_data'] = api_result['user_data']
        
        if not result['api_valid']:
            result['error'] = api_result['error']
        
        return result


async def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python validate_token.py <discord_token>")
        print("Example: python validate_token.py ")
        sys.exit(1)
    
    token = sys.argv[1]
    
    print("🔍 Validating Discord token...")
    print("=" * 50)
    
    try:
        async with TokenValidator() as validator:
            result = await validator.validate_comprehensive(token)
            
            # Display results
            print(f"Token: {result['token']}")
            print(f"Format Valid: {'✅' if result['format_valid'] else '❌'}")
            print(f"API Valid: {'✅' if result['api_valid'] else '❌'}")
            
            if result['user_id']:
                print(f"User ID: {result['user_id']}")
            
            if result['user_data']:
                user = result['user_data']
                print(f"Username: {user.get('username', 'Unknown')}#{user.get('discriminator', '0000')}")
                print(f"ID: {user.get('id', 'Unknown')}")
                print(f"Verified: {'✅' if user.get('verified', False) else '❌'}")
                print(f"MFA Enabled: {'✅' if user.get('mfa_enabled', False) else '❌'}")
                print(f"Email: {user.get('email', 'Not provided')}")
            
            if result['error']:
                print(f"Error: {result['error']}")
            
            # Exit with appropriate code
            if result['format_valid'] and result['api_valid']:
                print("\n✅ Token is valid!")
                sys.exit(0)
            else:
                print("\n❌ Token is invalid!")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
