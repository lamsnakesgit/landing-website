
const { app, safeStorage } = require('electron');
const fs = require('fs');
const path = require('path');

app.whenReady().then(() => {
    try {
        const userDataPath = '/Users/higherpower/Library/Application Support/Granola';
        const dekPath = path.join(userDataPath, 'storage.dek');
        if (fs.existsSync(dekPath)) {
            const encDek = fs.readFileSync(dekPath);
            const decDekBase64 = safeStorage.decryptString(encDek);
            const dek = Buffer.from(decDekBase64, 'base64');
            fs.writeFileSync('/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/decrypted_dek.key', dek);
            console.log('DEK_WRITTEN_SUCCESS');
        }
    } catch (e) {
        console.error('Failed to write DEK:', e);
    }
    app.exit(0);
});
