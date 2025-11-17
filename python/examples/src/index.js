const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;
const INSTANCE = process.env.INSTANCE || '1';

app.get('/', (req, res) => {
    res.json({
        message: 'Hello from Hopx!',
        instance: INSTANCE,
        timestamp: new Date().toISOString()
    });
});

app.get('/health', (req, res) => {
    res.json({ status: 'healthy', instance: INSTANCE });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT} (Instance ${INSTANCE})`);
});
