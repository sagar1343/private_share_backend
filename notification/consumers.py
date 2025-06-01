import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.scope["user"] = await self.get_user()
            user = self.scope["user"]

            if user is None or user.is_anonymous:
                await self.close(code=4001)
                return

            self.group_name = f"user-{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send(
                text_data=json.dumps(
                    {"message": f"Welcome {user.email}!", "event": "CONNECTED"}
                )
            )
        except Exception as e:
            print(f"WebSocket connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "event": "notifications",
                }
            )
        )

    @database_sync_to_async
    def get_user(self):
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth import get_user_model
            from django.contrib.auth.models import AnonymousUser
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

            User = get_user_model()
            query_string = self.scope["query_string"].decode()

            if not query_string or "token=" not in query_string:
                return AnonymousUser()

            token = query_string.split("token=")[-1]
            if not token:
                return AnonymousUser()

            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]

                user = User.objects.get(id=user_id)
                return user

            except (InvalidToken, TokenError) as e:
                return AnonymousUser()
            except User.DoesNotExist:
                return AnonymousUser()
            except Exception as e:
                return AnonymousUser()

        except Exception as e:
            return AnonymousUser()
