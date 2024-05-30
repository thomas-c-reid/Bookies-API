const config = {
    port: 3000,
    region: 'uk',
    APIKEY: '8898079a3451f9e0ac42b0da2c883644',
    sports_url: 'https://api.the-odds-api.com/v4/sports',
    sportsCsv: {
        url: 'data/sports.csv',
        fieldMapping: ['key', 'group', 'title', 'description', 'active', 'has_outrights']
    },
    oddsBySport: {
        url: 'data/oddsForSport.csv',
        fieldMapping: ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team', 'bookmakers']
    },
    eventsBySport: {
        url: 'data/eventsForSport.csv',
        fieldMapping: ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team']
    },
    oddsForEvent: {
        url: 'data/oddsForEvent.csv',
        fieldMapping: ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team', 'bookmakers']
    }

};

export default config
