import bettingService from '../services/bettingServices.js';
import csvService from '../utils/csvService.js'
import config from '../config.js'

const getAllSports = async (req, res) => {
    try {
        const response = await bettingService.getSportData();
        console.log(response);
        res.status(200).json(response);
    } catch (error) {
        console.error('Error fetching betting data:', error);
        res.status(500).json({ message: 'Error Fetching Betting Data' });
    }
};

const getOddsBySport = async (req, res) => {
    try {
        const sportsName = req.params.sport;
        const response = await bettingService.getOddsForSport(sportsName);
        res.status(200).json(response);
    } catch (error){
        console.log(`Error fetching Odds data for ${sportsName}`, error)
        res.status(500).json({message: 'Error fetching betting data'})
    }
};

const getEventsBySport = async (req, res) => {
    try {
        const sportName = req.params.sport;
        const response = await bettingService.getEventsForSport(sportName);
        // console.log(response);
        // csvService.csvSave(response, config.eventsBySport.url, config.eventsBySport.fieldMapping)
        res.status(200).json(response);
    } catch (error) {
        console.log(`Error fetching Event data for ${sportName}`, error);
        res.status(500).json({message: `Error fetching Event data for ${sportName}`});
    }
};

const getEventsBySportEventId = async (req, res) => {
    try {
        const sportName = req.params.sport;
        const eventId = req.params.eventId
        const response = await bettingService.getEventsForSportEventId(sportName, eventId);
        // csvService.csvSave(response, config.oddsForEvent.url, config.oddsForEvent.fieldMapping)
        res.status(200).json(response);
    } catch (error) {
        console.log(`Error fetching Event data for ${sportName}`, error);
        res.status(500).json({message: `Error fetching Event data for ${sportName} with eventId ${eventId}`});
    }
}

export default {
    getAllSports,
    getOddsBySport,
    getEventsBySport,
    getEventsBySportEventId
};