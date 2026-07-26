const { app, safeStorage } = require('electron');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

app.whenReady().then(async () => {
    try {
        const userDataPath = '/Users/higherpower/Library/Application Support/Granola';
        const dekPath = path.join(userDataPath, 'storage.dek');
        if (!fs.existsSync(dekPath)) {
            throw new Error('storage.dek not found');
        }
        
        // Decrypt the DEK
        const encDek = fs.readFileSync(dekPath);
        const decDekBase64 = safeStorage.decryptString(encDek);
        const dek = Buffer.from(decDekBase64, 'base64');
        
        // Decrypt supabase.json.enc
        const encSupabase = fs.readFileSync(path.join(userDataPath, 'supabase.json.enc'));
        const iv = encSupabase.subarray(0, 12);
        const tag = encSupabase.subarray(encSupabase.length - 16);
        const ciphertext = encSupabase.subarray(12, encSupabase.length - 16);
        
        const decipher = crypto.createDecipheriv('aes-256-gcm', dek, iv);
        decipher.setAuthTag(tag);
        const decryptedSupabase = Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString('utf8');
        
        console.log('--- SUPABASE CONFIGS ---');
        console.log(decryptedSupabase);
        console.log('------------------------');
        
    } catch (e) {
        console.error('Decryption failed:', e);
    }
    app.exit(0);
});
