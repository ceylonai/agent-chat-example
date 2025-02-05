import asyncio
import dataclasses

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
import socketio

# Initialize FastAPI
app = FastAPI()

# Add CORS Middleware for FastAPI routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO with allowed origins
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[
    "http://localhost:3000"
])
socket_app = socketio.ASGIApp(sio, app)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

# Store usernames
usernames = {}


# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    if sid in usernames:
        del usernames[sid]


@sio.event
async def set_username(sid, username):
    usernames[sid] = username
    await sio.emit("user_joined", {"username": username})
    print(f"{username} joined the chat")


@sio.event
async def message(sid, data):
    username = usernames.get(sid, "Unknown")
    print(f"Message from {username}: {data}")
    # Broadcast the message to all connected clients
    await sio.emit("response", {"username": username, "message": data})


# FastAPI route to serve the main page
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Room-related events
@sio.event
async def join_room(sid, room):
    await sio.enter_room(sid, room)
    await sio.emit("room_joined", {"room": room, "username": usernames.get(sid, "Unknown")}, room=room)


@sio.event
async def leave_room(sid, room):
    await sio.leave_room(sid, room)
    await sio.emit("room_left", {"room": room, "username": usernames.get(sid, "Unknown")}, room=room)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(admin.start_agent(b"", [worker_1, worker_2, worker_3]))


@admin.on_connect("*")
async def on_connect(topic, agent: AgentDetail):
    await asyncio.sleep(2)
    print(f"Agent connected: {agent.name}")
    print(f"Agent connected: {agent.id}")
    usernames[agent.id] = agent.name
    await sio.emit("user_joined", {"username": agent.name})
    # Broadcast the message to all connected clients
    await sio.emit("response", {"username": agent.name, "message": f"Agent {agent.name} connected"})


@worker_1.on(dict)
async def on_message_1(data, sender: AgentDetail, time):
    print(f"Message from {sender.name}  - {data['message']}")
    # Broadcast the message to all connected clients
    await sio.emit("response",
                   {"username": worker_1.details().name,
                    "message": f'Message From {worker_1.details().name} - {data["message"]}'})


@admin.on_run()
async def on_run(input):
    print("Admin is running")
    while True:
        await admin.broadcast_message({"message": "Admin is running"})
        await asyncio.sleep(1)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(socket_app, host="0.0.0.0", port=3000)
