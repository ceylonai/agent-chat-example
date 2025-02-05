from typing import Dict, Any

class SocketHandler:
    def __init__(self, sio):
        self.sio = sio
        self.connected_users: Dict[str, Any] = {}

    async def handle_connect(self, sid: str, environ: Dict):
        self.connected_users[sid] = {
            'sid': sid,
            'user_agent': environ.get('HTTP_USER_AGENT', '')
        }
        await self.sio.emit('user_connected',
                           {'message': f'User {sid} connected'},
                           skip_sid=sid)

    async def handle_disconnect(self, sid: str):
        if sid in self.connected_users:
            del self.connected_users[sid]
            await self.sio.emit('user_disconnected',
                              {'message': f'User {sid} disconnected'})
