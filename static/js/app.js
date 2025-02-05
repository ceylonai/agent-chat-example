const socket = io();
const messagesDiv = document.getElementById("messages");
const messageInput = document.getElementById("message-input");

let username = localStorage.getItem("username") || prompt("Enter your name:");
localStorage.setItem("username", username);

// Send username to the server
socket.emit("set_username", username);

// Connection event
socket.on("connect", () => {
    console.log("Connected to server");
    appendMessage("System", "Connected to server");
});

// Receiving messages
socket.on("response", (data) => {
    appendMessage(data.username, data.message);
});

// Notify when a user joins
socket.on("user_joined", (data) => {
    appendMessage("System", `${data.username} joined the chat`);
});

// Disconnect event
socket.on("disconnect", () => {
    console.log("Disconnected from server");
    appendMessage("System", "Disconnected from server");
});

// Send message function
function sendMessage() {
    const message = messageInput.value;
    if (message.trim()) {
        socket.emit("message", message);
        messageInput.value = "";
    }
}

// Helper function to append messages to the chat
function appendMessage(sender, message) {
    const messageElement = document.createElement("div");
    messageElement.textContent = `${sender}: ${message}`;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
