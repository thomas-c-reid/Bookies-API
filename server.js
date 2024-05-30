import express, { json } from 'express';
import config from './config.js';
import BettingRoutes from './routes/bettingRoutes.js'

const app = express();
const PORT = config.port;

app.use(json());
app.use('/betting', BettingRoutes);

app.listen(PORT, () => {
    console.log(`Listening on port${PORT}`)
});