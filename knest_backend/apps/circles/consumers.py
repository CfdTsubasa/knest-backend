import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import CircleChat, CircleMembership, CircleChatRead
from django.core.exceptions import ObjectDoesNotExist

class CircleChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.circle_id = self.scope['url_route']['kwargs']['circle_id']
        self.room_group_name = f'chat_{self.circle_id}'
        self.user = self.scope['user']

        # メンバーシップの確認
        if not await self.is_circle_member():
            await self.close()
            return

        # グループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # オンライン状態を通知
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_online',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'display_name': self.user.display_name,
                }
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # オフライン状態を通知
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_offline',
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username,
                        'display_name': self.user.display_name,
                    }
                }
            )
            
            # グループから離脱
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            # メッセージの保存と送信
            message = await self.save_message(data['content'], data.get('reply_to'))
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(message.id),
                        'content': message.content,
                        'sender': {
                            'id': str(message.sender.id),
                            'username': message.sender.username,
                            'display_name': message.sender.display_name,
                            'avatar_url': message.sender.avatar_url,
                        },
                        'created_at': message.created_at.isoformat(),
                        'is_system_message': message.is_system_message,
                        'reply_to': await self.get_reply_to_data(message.reply_to) if message.reply_to else None,
                    }
                }
            )
        elif message_type == 'typing':
            # タイピング状態の通知
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username,
                        'display_name': self.user.display_name,
                    }
                }
            )
        elif message_type == 'read':
            # 既読の更新
            await self.update_read_status()
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read',
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username,
                        'display_name': self.user.display_name,
                    }
                }
            )

    async def chat_message(self, event):
        """メッセージをクライアントに送信"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))

    async def user_typing(self, event):
        """タイピング状態をクライアントに送信"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user']
        }))

    async def message_read(self, event):
        """既読状態をクライアントに送信"""
        await self.send(text_data=json.dumps({
            'type': 'read',
            'user': event['user']
        }))

    async def user_online(self, event):
        """オンライン状態をクライアントに送信"""
        await self.send(text_data=json.dumps({
            'type': 'online',
            'user': event['user']
        }))

    async def user_offline(self, event):
        """オフライン状態をクライアントに送信"""
        await self.send(text_data=json.dumps({
            'type': 'offline',
            'user': event['user']
        }))

    @database_sync_to_async
    def is_circle_member(self):
        """サークルのメンバーかどうかを確認"""
        return CircleMembership.objects.filter(
            user=self.user,
            circle_id=self.circle_id,
            status='active'
        ).exists()

    @database_sync_to_async
    def save_message(self, content, reply_to_id=None):
        """メッセージを保存"""
        reply_to = None
        if reply_to_id:
            try:
                reply_to = CircleChat.objects.get(id=reply_to_id)
            except ObjectDoesNotExist:
                pass

        return CircleChat.objects.create(
            circle_id=self.circle_id,
            sender=self.user,
            content=content,
            reply_to=reply_to
        )

    @database_sync_to_async
    def update_read_status(self):
        """既読状態を更新"""
        CircleChatRead.objects.update_or_create(
            user=self.user,
            circle_id=self.circle_id,
            defaults={'last_read': timezone.now()}
        )

    @database_sync_to_async
    def get_reply_to_data(self, reply_to):
        """返信先メッセージのデータを取得"""
        if not reply_to:
            return None
            
        return {
            'id': str(reply_to.id),
            'content': reply_to.content[:100],
            'sender': {
                'id': str(reply_to.sender.id),
                'username': reply_to.sender.username,
                'display_name': reply_to.sender.display_name,
            }
        } 