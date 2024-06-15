const config = {
    port: 3000,
    region: 'uk',
    sports_url: 'https://api.the-odds-api.com/v4/sports',
    baseLocalhostUrl: 'http://localhost:3000/betting/sports',
    selectedSports: ['tennis_wta_french_open', 'blah blah'],
    euros: ['soccer_uefa_european_championship'],
    legacyDatasetUrl: '../../Datasets/Bookies-Data',

    sportsCsv: {
        url: '../data/sports.csv',
        fieldMapping: ['key', 'group', 'title', 'description', 'active', 'has_outrights']
    },

    oddsBySport: {
        url: '../data/oddsForSport.csv',
        fieldMapping: ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team', 'bookmakers']
    },

    eventsBySport: {
        url: '../data/eventsForSport/',
        fieldMapping: ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team']
    },

    oddsForEvent: {
        url: '../data/oddsForEvent/',
        fieldMapping: ['id', 'sport_key', 'sport_title', 'commence_time', 'home_team', 'away_team', 'bookmakers']
    },
    


};

export default config
