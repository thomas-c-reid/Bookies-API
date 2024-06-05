const express = require('express');
const axios = require('axios');
require('dotenv').config();
const { Parser } = require('json2csv');
const fs = require('fs');

const app = express();
const port = 3000;
const CSV_BASE_URL = 'odds_data'
const HISTORICAL_BASE_URL = 'historical'


// TODO: 
// we need to be able to save all the sports within a selected folder


app.use(express.json());

// endpoints needed
// /sports
base_url = 'https://api.the-odds-api.com';

// Sports Endpoint - This give an indication of all the leagues we can get odds on 
app.get('/sports', async (req, res) =>{
    try {
        url2 = `${base_url}/v4/sports/?apiKey=${APIKEY}`
        response = await axios.get(url2);

        possibleArray = response.data;
        console.log('Type of response.data:', typeof response.data);

        if (Array.isArray(possibleArray)) {
          data = possibleArray;
          console.log('Extracted array:', typeof data);
        } else {
          console.error('Expected an array but got:', typeof possibleArray);
        }

        const fields = ['key', 'group', 'title', 'description', 'active', 'has_outrights'];
        const opts = { fields };
        const parser = new Parser(opts);
        const csv = parser.parse(data);

        fs.writeFileSync('sports.csv', csv);
        console.log('Successfully written to sports CSV');

        // await csvWriter.writeRecords(data);
    } catch (error) {
        console.error('Error message: ', error.message);
        console.error('Error stack: ', error.stack);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/sports/:sport/odds', async (req, res) => {
    try {

        const sport = req.params.sport // This will have to change to take in either an array of sports or just the variable
        const region = req.query.region
        // if we want to define a list of sports to take in it would look like this
        // sports = req.query.sports
        // curl http://localhost...odds?sports=sport_1,sport_2,etc...

        //other params
        //
        // const markets = req.query.markets
        // const dateFormat = req.query.dateFormat
        // const oddsFormat = req.query.oddsFormat
        // const eventIds = req.query.eventIds
        // const bookmakers = req.query.bookmakers
        // const commenceTimeFrom = req.query.commenceTimeFrom
        // const commenceTimeTo = req.query.commenceTimeTo

        url2 = `${base_url}/v4/sports/${sport}/odds?apiKey=${APIKEY}&regions=${region}`
        console.log('URL: ', url2)
        response = await axios.get(url2);

        const data = response.data.map(event => {
            return {
                ...event,
                bookmakers: JSON.stringify(event.bookmakers)
            };
        });


        const fields = ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team', 'bookmakers'];
        const opts = { fields };
        const parser = new Parser(opts);
        const csv = parser.parse(data);

        csv_url = `${CSV_BASE_URL}/${sport}.csv`
        fs.writeFileSync(csv_url, csv);
        console.log('Successfully written to sports CSV');
        res.json(response.data);



    } catch (error) {

    }
});

app.get('/sports/:sport/events', async (req, res) => {
    try {
        const sport = req.params.sport;

        // const dateFormat = req.query.markets
        // const eventIds = req.query.eventIds
        // const oddsFormat = req.query.markets
        // const bookmakers = req.query.markets

        const url = `${base_url}/v4/sports/${sport}/events?apiKey=${APIKEY}`;
        console.log('URL: ', url);
        response = await axios.get(url);

        const fields = ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team'];
        const opts = { fields };
        const parser = new Parser(opts);
        const csv = parser.parse(data);

        csv_url = `${CSV_BASE_URL}/${sport}-event.csv`
        fs.writeFileSync(csv_url, csv);
        console.log('Successfully written to sports-event CSV');
        res.json(response.data);

    } catch (error){

    }
});

app.get('/sports/:sport/events/:eventId/odds', async (req, res) => {
    try {
        const sport = req.params.sport;
        const eventId = req.params.eventId;
        const region = req.query.region;

        // const markets = req.query.markets
        // const dateFormat = req.query.markets
        // const oddsFormat = req.query.markets
        // const bookmakers = req.query.markets

        const url = `${base_url}/v4/sports/${sport}/events/${eventId}/odds?apiKey=${APIKEY}&regions=${region}`;
        console.log('URL: ', url);
        response = await axios.get(url);


        const fields = ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team', 'bookmakers'];
        const opts = { fields };
        const parser = new Parser(opts);
        const csv = parser.parse(response.data);

        csv_url = `${CSV_BASE_URL}/${sport}-${eventId}.csv`
        fs.writeFileSync(csv_url, csv);
        console.log('Successfully written to sports CSV');
        res.json(response.data);

    } catch (error){

    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`)
})

// Do i need a section where i define all the routes???
