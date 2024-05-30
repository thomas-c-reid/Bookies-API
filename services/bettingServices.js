import config from '../config.js';
import axios from 'axios';

const getSportData = async () => {
    const url = `${config.sports_url}/?apiKey=${config.APIKEY}`;
    const response = await axios.get(url);
    return response.data;
};

const getOddsForSport = async (sportsName) => {
    const url = `${config.sports_url}/${sportsName}/odds?apiKey=${config.APIKEY}&regions=${config.region}`;
    const response = await axios.get(url);
    return response.data;
};

const getEventsForSport = async (sportsName) => {
    const url = `${config.sports_url}/${sportsName}/events?apiKey=${config.APIKEY}`;
    const response = await axios.get(url);
    return response.data;
};

const getEventsForSportEventId = async (sportsName, eventId) => {
    const url = `${config.sports_url}/${sportsName}/events/${eventId}/odds?apiKey=${config.APIKEY}&regions=${config.region}`;
    const response = await axios.get(url);
    console.log(response)
    return response.data;
};

export default {
    getSportData,
    getOddsForSport,
    getEventsForSport,
    getEventsForSportEventId
}