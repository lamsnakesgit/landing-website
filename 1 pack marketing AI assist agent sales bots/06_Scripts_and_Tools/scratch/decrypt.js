
const { app, safeStorage } = require('electron');
const fs = require('fs');

app.whenReady().then(() => {
    try {
        const encData = fs.readFileSync('/Users/higherpower/Library/Application Support/Granola/supabase.json.enc');
        const decrypted = safeStorage.decryptString(encData);
        console.log('DECRYPTED_START' + decrypted + 'DECRYPTED_END');
    } catch (e) {
        console.error('Decryption failed:', e);
    }
    app.exit(0);
});
