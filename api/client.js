import axios from 'axios';
import config from '../config.js';
import csvService from '../utils/csvService.js'
import jsonHelpers from '../utils/jsonHelpers.js';
import fileHelpers from '../utils/fileHelpers.js';

const fetchData = async () => {

    let availableFilteredSportsArray = [];
    let futureEvents = [];
    try {

        const sportsResponse = await axios.get(config.baseLocalhostUrl);
        if (sportsResponse.data) {
            console.log('Sports data fetched');
            const currentSportArray = jsonHelpers.extractKeyFromSportsArray(sportsResponse.data)
            availableFilteredSportsArray = jsonHelpers.findIntersection(currentSportArray, config.euros)
            csvService.csvSave(sportsResponse.data, config.sportsCsv.url, config.sportsCsv.fieldMapping);
        } else {
            console.log('No Data Received');
        }
    } catch (error) {
        console.log(error.stack)
    }


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

            const sportOdds = []

            for (const event of futureEvents){
                try{
                    // This is where you will call next endpoint
                    // fileHelpers.saveToLegacyDateFolder(sport)
                    console.log(`${config.legacyDatasetUrl}/sport`)

                    const eventOddsResponse = await axios.get(`${config.baseLocalhostUrl}/${sport}/events/${event.id}/odds`);
                    // const eventOddsMarket = eventOddsResponse.data.bookmakers
                    sportOdds.push(eventOddsResponse.data);
                    // console.log(eventOddsResponse.data)
                    // console.log(eventOddsMarket)

                    // if there are < 3 bookmakers available. Dont save to CSV
                    // the more bookmakers - the more reliable the large data is (for calculating good bet)

                    // const url = `${config.oddsForEvent.url}/${sport}`
                    // fileHelpers.createDirectoryIfNotExist(url)
        
                    // you want to extract all 'commence_time' and only store the ones in which happen after commence_time
                    // csvService.csvSave(eventOddsResponse.data, `${config.oddsForEvent.url}/${sport}/${event.id}`, config.oddsForEvent.fieldMapping)
                } catch (error) {
                    // Failed to get data
                    console.log(error.stack)
                };
            };

            // const url = `${config.oddsForEvent.url}`
            // fileHelpers.createDirectoryIfNotExist(url)

            csvService.csvSave(sportOdds, `${config.oddsForEvent.url}/${sport}.csv`, config.oddsForEvent.fieldMapping)
            console.log(`successfully written to ${sport} CSV`)
        } catch (error) {
            // Failed to get data
            console.log(error.stack)
        };
    };
    console.log()
};

const testLegacy = () => {
    fileHelpers.saveToLegacyDateFolder();
};

testLegacy();
// fetchData();



// TODO
// make a func (put in utils/csvService) that will remove all CSV files saved in /data when this script initially runs
// ----> This function should run fileHelpers.saveToLegacyDateFolder() and move all CSV files in the legacy data folder
// change saveCsv function so for oddsForEvent it saves all the 
// function to -if betting data already exists for a sport. Move the file over to the legacy-data and then save the new data in its place