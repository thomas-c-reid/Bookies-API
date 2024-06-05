import config from '../../config.js'
import axios from 'axios';
import env from '../../env.js';

const getSportData = async () => {
    const url = `${config.sports_url}/?apiKey=${env.APIKEY}&all=true`;
    const response = await axios.get(url);
    return response.data;
};

const getOddsForSport = async (sportsName) => {
    const url = `${config.sports_url}/${sportsName}/odds?apiKey=${env.APIKEY}&regions=${config.region}`;
    const response = await axios.get(url);
    return response.data;
};

const getEventsForSport = async (sportsName) => {
    const url = `${config.sports_url}/${sportsName}/events?apiKey=${env.APIKEY}`;
    const response = await axios.get(url);
    return response.data;
};

const getEventsForSportEventId = async (sportsName, eventId) => {
    const url = `${config.sports_url}/${sportsName}/events/${eventId}/odds?apiKey=${env.APIKEY}&regions=${config.region}`;
    const response = await axios.get(url);
    return response.data;
};

export default {
    getSportData,
    getOddsForSport,
    getEventsForSport,
    getEventsForSportEventId
}