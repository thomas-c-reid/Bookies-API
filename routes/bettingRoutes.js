import { Router } from 'express';
import bettingcontroller from '../controllers/bettingcontroller.js';

const router = Router();

router.get('/sports', bettingcontroller.getAllSports);
router.get('/sports/:sport/odds', bettingcontroller.getOddsBySport)
router.get('/sports/:sport/events', bettingcontroller.getEventsBySport)
router.get('/sports/:sport/events/:eventId/odds', bettingcontroller.getEventsBySportEventId)

export default router;