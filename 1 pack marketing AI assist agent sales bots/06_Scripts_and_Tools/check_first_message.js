const API_URL = "https://evolutionapi.aiconicvibe.store";
const API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
const INSTANCE = "bee 133 1121 687 35 20";

async function checkFirst() {
    try {
        const res = await fetch(`${API_URL}/chat/findMessages/${encodeURIComponent(INSTANCE)}`, {
            method: "POST",
            headers: { 
                "apikey": API_KEY,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                where: { remoteJid: "120363408043123577@g.us" }
            })
        });
        const data = await res.json();
        if (data.messages && data.messages.records && data.messages.records.length > 0) {
            console.log("Пример сообщения:", JSON.stringify(data.messages.records[0], null, 2));
        } else {
            console.log("Сообщения не найдены");
        }
    } catch(e) {
        console.log("Ошибка:", e.message);
    }
}
checkFirst();
