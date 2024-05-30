import axios from 'axios';
import config from './config.js';
import csvService from './utils/csvService.js'
import jsonHelpers from './utils/jsonHelpers.js';
import fileHelpers from './utils/fileHelpers.js';

const fetchData = async () => {

    let availableFilteredSportsArray = [];
    let futureEvents = [];
    try {
        const sportsResponse = await axios.get(config.baseLocalhostUrl);
        if (sportsResponse.data) {
            console.log('Sports data fetched');
            const currentSportArray = jsonHelpers.extractKeyFromSportsArray(sportsResponse.data)
            availableFilteredSportsArray = jsonHelpers.findIntersection(currentSportArray, config.selectedSports)
            csvService.csvSave(sportsResponse.data, config.sportsCsv.url, config.sportsCsv.fieldMapping);
        } else {
            console.log('No Data Received');
        }
    } catch (error) {
        console.log(error)
    }
    // console.log(availableFilteredSportsArray)
    // for (const sport of availableFilteredSportsArray){
    //     console.log(sport)
    //     try{
    //         // This is where you will call next endpoint
    //         const sportsOddsResponse = await axios.get(`${config.baseLocalhostUrl}/${sport}/odds`);
    //         csvService.csvSave(sportsOddsResponse, config.oddsBySport.url, config.oddsBySport.fieldMapping)
    //     } catch (error) {
    //         // Failed to get data
    //         console.log(error)
    //     };
    // };
    for (const sport of availableFilteredSportsArray){
        try{
            // This is where you will call next endpoint
            const sportsEventsResponse = await axios.get(`${config.baseLocalhostUrl}/${sport}/events`);
            console.log('Event data fetched');
            const now = new Date();
            futureEvents = sportsEventsResponse.data.filter(event => {
                const eventDate = new Date (event.commence_time);
                return eventDate > now;
            });

            // you want to extract all 'commence_time' and only store the ones in which happen after commence_time
            csvService.csvSave(futureEvents, `${config.eventsBySport.url}/${sport}.csv`, config.eventsBySport.fieldMapping)

            for (const event of futureEvents){
                try{
                    // This is where you will call next endpoint
                    const eventOddsResponse = await axios.get(`${config.baseLocalhostUrl}/${sport}/events/${event.id}/odds`);
                    console.log(eventOddsResponse.data)

                    const url = `${config.oddsForEvent.url}/${sport}`
                    fileHelpers.createDirectoryIfNotExist(url)
        
                    // you want to extract all 'commence_time' and only store the ones in which happen after commence_time
                    csvService.csvSave(futureEvents, `${config.oddsForEvent.url}/${sport}/${event.id}`, config.eventsBySport.fieldMapping)
                } catch (error) {
                    // Failed to get data
                    console.log(error)
                };
            };
        } catch (error) {
            // Failed to get data
            console.log(error)
        };
    };
};

const tester = () => {
    const filenames = ['routes', 'services'];
    for (const filename of filenames){
        const boo = fileHelpers.createDirectoryIfNotExist(filename);
    }
}

fetchData();
// tester();

// TODO
// add to the url of the endpoints to get the data returned in 