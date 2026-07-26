const API_URL = "https://evolutionapi.aiconicvibe.store";
const API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
const INSTANCE = "bee 133 1121 687 35 20";
const GROUP_ID = "120363408043123577@g.us";

async function checkGroup() {
    try {
        console.log("🔍 Ищем информацию о группе...");
        const res = await fetch(`${API_URL}/group/findGroupInfos/${encodeURIComponent(INSTANCE)}?groupJid=${encodeURIComponent(GROUP_ID)}`, {
            headers: { "apikey": API_KEY }
        });
        const data = await res.json();
        console.log("Название группы:", data.subject || "Не найдено (или это не группа)");
        console.log("Кол-во участников:", data.participants ? data.participants.length : "Неизвестно");
    } catch(e) {
        console.log("Ошибка получения инфо группы:", e.message);
    }
}
checkGroup();
