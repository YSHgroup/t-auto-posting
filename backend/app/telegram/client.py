"""
Telegram client service using pyrogram
"""
import os
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, SessionPasswordNeeded, AuthBytesInvalid, RpcError
from typing import List, Optional, Dict, Any
import asyncio
import time
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    """Telegram Client wrapper for all Telegram operations"""
    
    def __init__(self, session_string: Optional[str] = None):
        self.api_id = settings.TELEGRAM_API_ID
        self.api_hash = settings.TELEGRAM_API_HASH
        self.phone_number = settings.TELEGRAM_PHONE_NUMBER
        self.session_string = session_string
        self.client: Optional[Client] = None
        self.is_connected = False
    
    def _get_client(self) -> Client:
        """Get or create Telegram client"""
        if self.client is None:
            self.client = Client(
                name="telegram_bot_session",
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_string=self.session_string if self.session_string else "user_session",
                in_memory=True if self.session_string else False
            )
        return self.client
    
    async def _ensure_connected(self):
        """Ensure client is connected"""
        if not self.is_connected:
            client = self._get_client()
            if not await client.connect():
                raise RuntimeError("Failed to connect to Telegram")
            self.is_connected = True
    
    async def _ensure_disconnected(self):
        """Ensure client is disconnected"""
        if self.is_connected and self.client:
            await self.client.disconnect()
            self.is_connected = False
    
    async def login_with_phone(self, phone: str) -> bool:
        """
        Start login process with phone number.
        Sends code to Telegram app.
        Returns True if code was sent successfully.
        """
        try:
            self.phone_number = phone
            client = self._get_client()
            await client.connect()
            self.is_connected = True
            
            # Send code to phone
            sent_code = await client.send_code(phone)
            logger.info(f"Code sent to {phone}")
            
            return True
        except RpcError as e:
            logger.error(f"Telegram RPC error: {e}")
            raise
        except Exception as e:
            logger.error(f"Telegram login error: {e}")
            raise
    
    async def verify_code(self, phone: str, code: str) -> Optional[str]:
        """
        Verify login code.
        Returns session string if successful.
        May raise SessionPasswordNeeded if 2FA is enabled.
        """
        try:
            client = self._get_client()
            if not self.is_connected:
                await client.connect()
                self.is_connected = True
            
            # Sign in with code
            user = await client.sign_in(phone, code)
            logger.info(f"Signed in as {user.first_name}")
            
            # Export session string for later use
            session_string = await client.export_session_string()
            return session_string
        except SessionPasswordNeeded:
            logger.info("2FA password required")
            raise
        except RpcError as e:
            logger.error(f"Telegram RPC error: {e}")
            raise
        except Exception as e:
            logger.error(f"Code verification error: {e}")
            raise
    
    async def verify_2fa(self, password: str) -> Optional[str]:
        """Verify 2FA password and get session string"""
        try:
            client = self._get_client()
            if not self.is_connected:
                await client.connect()
                self.is_connected = True
            
            await client.check_password(password)
            
            # Get session string
            session_string = await client.export_session_string()
            return session_string
        except Exception as e:
            logger.error(f"2FA verification error: {e}")
            raise
    
    async def search_groups(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for public Telegram groups by keyword.
        Uses Telegram's search_global API.
        
        Returns list of group info dicts
        """
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            results = []
            try:
                # Search for public groups/channels
                async for dialog in client.search_global(query, limit=limit):
                    if dialog.is_group or dialog.is_supergroup:
                        results.append({
                            "id": dialog.id,
                            "title": dialog.title,
                            "username": dialog.username,
                            "type": "group" if dialog.is_group else "supergroup",
                            "is_public": bool(dialog.username),
                            "members_count": dialog.members_count if hasattr(dialog, 'members_count') else 0,
                            "is_verified": dialog.is_verified if hasattr(dialog, 'is_verified') else False,
                        })
            except Exception as inner_e:
                logger.warning(f"Search global error: {inner_e}")
            
            return results
        except Exception as e:
            logger.error(f"Group search error: {e}")
            return []
    
    async def get_group_info(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed group information"""
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            chat = await client.get_chat(group_id)
            
            info = {
                "id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "description": chat.description or "",
                "members_count": chat.members_count if hasattr(chat, 'members_count') else 0,
                "is_supergroup": chat.is_supergroup if hasattr(chat, 'is_supergroup') else False,
                "is_public": chat.username is not None,
                "is_verified": chat.is_verified if hasattr(chat, 'is_verified') else False,
                "is_restricted": chat.is_restricted if hasattr(chat, 'is_restricted') else False,
                "photo_id": str(chat.photo.file_id) if chat.photo else None,
            }
            
            return info
        except Exception as e:
            logger.error(f"Get group info error: {e}")
            return None
    
    async def get_recent_messages(self, group_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent messages from a group"""
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            messages = []
            async for msg in client.get_chat_history(group_id, limit=limit):
                messages.append({
                    "id": msg.message_id,
                    "text": msg.text or "",
                    "from_user_id": msg.from_user.id if msg.from_user else None,
                    "from_user_name": msg.from_user.username if msg.from_user else None,
                    "from_user_first_name": msg.from_user.first_name if msg.from_user else None,
                    "date": int(msg.date.timestamp()) if msg.date else None,
                    "reply_to_message_id": msg.reply_to_message_id,
                    "has_media": msg.media is not None,
                })
            
            return messages
        except Exception as e:
            logger.error(f"Get messages error: {e}")
            return []
    
    async def send_message(self, group_id: int, text: str, max_retries: int = 5) -> Optional[str]:
        """
        Send message to a group with retry logic.
        Handles FloodWait errors with exponential backoff.
        """
        retries = 0
        last_error = None
        
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            while retries < max_retries:
                try:
                    message = await client.send_message(group_id, text)
                    logger.info(f"Message sent to group {group_id}: {message.message_id}")
                    return str(message.message_id)
                
                except FloodWait as fw:
                    wait_seconds = fw.value
                    logger.warning(f"FloodWait: waiting {wait_seconds} seconds")
                    
                    if retries < max_retries - 1:
                        await asyncio.sleep(wait_seconds)
                        retries += 1
                    else:
                        raise
                
                except Exception as e:
                    last_error = e
                    raise
        
        except FloodWait as fw:
            logger.error(f"FloodWait after retries: {fw.value}s")
            raise
        except Exception as e:
            logger.error(f"Send message error: {e}")
            raise
    
    async def delete_message(self, group_id: int, message_id: int) -> bool:
        """Delete a message from a group"""
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            await client.delete_messages(group_id, message_id)
            logger.info(f"Message deleted: {message_id}")
            
            return True
        except Exception as e:
            logger.warning(f"Delete message error: {e}")
            return False
    
    async def get_member_count(self, group_id: int) -> int:
        """Get group member count"""
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            chat = await client.get_chat(group_id)
            count = chat.members_count if hasattr(chat, 'members_count') else 0
            
            return count
        except Exception as e:
            logger.error(f"Get member count error: {e}")
            return 0
    
    async def join_group(self, group_link: str) -> bool:
        """Join a group via link"""
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            await client.join_chat(group_link)
            logger.info(f"Joined group: {group_link}")
            
            return True
        except Exception as e:
            logger.error(f"Join group error: {e}")
            return False
    
    async def leave_group(self, group_id: int) -> bool:
        """Leave a group"""
        try:
            await self._ensure_connected()
            client = self._get_client()
            
            await client.leave_chat(group_id)
            logger.info(f"Left group: {group_id}")
            
            return True
        except Exception as e:
            logger.error(f"Leave group error: {e}")
            return False
    
    async def close(self):
        """Close the Telegram client connection"""
        try:
            await self._ensure_disconnected()
        except Exception as e:
            logger.error(f"Error closing Telegram client: {e}")


# Singleton instance
_telegram_service: Optional[TelegramService] = None

def get_telegram_service(session_string: Optional[str] = None) -> TelegramService:
    """Get Telegram service instance"""
    return TelegramService(session_string=session_string)
