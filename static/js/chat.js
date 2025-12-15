let socket = null;

function startChatWS(groupId) {
    socket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + groupId + '/'
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
}

function sendChatWS(content) {
    if (!content.trim()) return;

    socket.send(JSON.stringify({
        content: content
    }));
}
