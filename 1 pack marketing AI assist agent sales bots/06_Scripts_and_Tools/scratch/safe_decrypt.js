
const { safeStorage } = require('electron');
const fs = require('fs');
try {
    const encData = fs.readFileSync('/Users/higherpower/Library/Application Support/Granola/supabase.json.enc');
    const decrypted = safeStorage.decryptString(encData);
    console.log('DECRYPTED_START' + decrypted + 'DECRYPTED_END');
} catch (e) {
    console.error('Direct decryption failed:', e);
}
