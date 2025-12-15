let socket = null;

function startChatWS(groupId) {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";

    socket = new WebSocket(
        protocol + "://" + window.location.host + "/ws/chat/" + groupId + "/"
    );

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const ul = document.querySelector(".messages");

        const li = document.createElement("li");

        if (data.is_me) {
            li.classList.add("chat-bubble", "receiver");
        } else {
            li.classList.add("chat-bubble", "sender");
        }

        li.innerHTML = `
            ${data.sender ? `<strong>${data.sender}:</strong> ` : ""}
            ${data.content}
            <em style="display:block; font-size:0.75rem; margin-top:4px;">
                (${new Date(data.timestamp).toLocaleString()})
            </em>
        `;

        ul.appendChild(li);
        ul.scrollTop = ul.scrollHeight;
    };

    socket.onclose = function () {
        console.warn("WebSocket cerrado");
    };

    socket.onerror = function (err) {
        console.error("WebSocket error", err);
    };
}

function sendChatWS(content) {
    if (!content.trim()) return;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn("WebSocket no está listo");
        return;
    }

    socket.send(JSON.stringify({
        content: content
    }));
}
