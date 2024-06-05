const processFileContents = (fileContents) => {
    /**
     * The point of this function is to take the live betting data for each sporting event for a certain sport
     * and output to a CSV the best bet information
     * {bookie: '888', type: 'h2h', name: 'home', price: '1.1', mean_price_for: '', mean_price_against: '', number_of_bookies: '', actual_metric_from_python: '', timestamp: 'just for having as reference in future data'}
     * 
     * Checks:
     * less than 3 bookies
     * 
     * TODO:
     * need to add lots of checks in: less than 2 bookies BREAK
    */
    // for (const event of fileContents) {
    //     console.log('-------------------------------')
    //     const bookmakersArray = JSON.parse(event.bookmakers);
    //     const numberOfBookmakers = bookmakersArray.length;
    //     const margin = 0.05;

    //     const eventJsonFor = {};
    //     const eventJsonAgainst = {};

    //     const bestBookieFor = null;
    //     const bestBookieAgainst = null;

    //     const timestampFor = null;
    //     const timestampAgainst = null;

    //     const prices_for = [];
    //     const prices_against = [];

    //     const bestPriceFor = 0;
    //     const bestPriceAgainst = 0;

    //     for (const bookmaker of bookmakersArray) {

    //         console.log('+++++++++++++')
    //         // console.log(bookmaker.key)
    //         bookmaker.markets.forEach((market) => {
    //             // need to make sure you have a way of storing all the different forms of data
    //             if (market.key == 'h2h'){
    //                 // console.log('Outcomes:', market.outcomes); // This will now properly display the outcomes array
    //                 if (market.outcomes[0] > bestPriceFor){
    //                     bestPriceFor = market[0].outcomes;
    //                     bestBookieFor = bookmaker.key;
    //                     let timestampFor = market[0].last_update;
    //                 };
                    
    //                 if (market.outcomes[1] > bestPriceAgainst) {
    //                     bestPriceAgainst = market[1].outcomes;
    //                     bestBookieAgainst = bookmaker.key;
    //                     timestampAgainst = market[1].last_update
    //         }}})};
    //     // {mean_price_for: '', mean_price_against: '', number_of_bookies: '', actual_metric_from_python: '', timestamp: 'just for having as reference in future data'}

    //     eventJsonFor['bookie'] = bestBookieFor; //will be needed to convert to a categorical encoding
    //     eventJsonAgainst['bookie'] = bestBookieAgainst; //will be needed to convert to a categorical encoding

    //     eventJsonFor['type'] = 'h2h'; //same again - probs just random selection
    //     eventJsonAgainst['type'] = 'h2h'; //same again - probs just random selection

    //     eventJsonFor['name'] = 'home'; // just for keeping track - defo remove means fuck all
    //     eventJsonAgainst['name'] = 'away'; // just for keeping track - defo remove means fuck all

    //     eventJsonFor['price'] = bestPriceFor; // important. Probs dont touch
    //     eventJsonAgainst['price'] = bestPriceAgainst; // important. Probs dont touch

    //     const sum_for = prices_for.reduce((partial_sum, current_num) => partial_sum + current_num, 0)
    //     const mean_for = sum_for / prices_for.length;
    //     eventJsonAgainst['mean_price_for'] = mean_for;

    //     const sum_against = prices_against.reduce((patrial_sum, current_num) => patrial_sum + current_num, 0)
    //     const mean_against = sum_against / prices_against.length;
    //     eventJsonAgainst['mean_price_against'] = mean_against;
        
    //     eventJsonFor['margin_for'] = ((1 / mean_for - margin) * bestPriceFor) - 1;
    //     eventJsonAgainst['margin_against'] = ((1 / mean_against - margin) * bestPriceAgainst) - 1;

    //     eventJsonFor['number_of_bookies'] = numberOfBookmakers; //
    //     eventJsonAgainst['number_of_bookies'] = numberOfBookmakers; //

    //     eventJsonFor['timestamp'] = TimestampFor; // will need removed at the end
    //     eventJsonAgainst['timestamp'] = timestampAgainst; //
    //     // Add averageFor calc
    //     // Add averageAgainst calc
    //     // addOtherPythonMetric



    //     console.log(eventJsonFor)
    //     console.log(eventJsonAgainst)
    // };

    for (const event of fileContents) {
        console.log('-------------------------------');
        const bookmakersArray = JSON.parse(event.bookmakers);
        const numberOfBookmakers = bookmakersArray.length;
        const margin = 0.05;
    
        let bestPriceFor = 0;
        let bestPriceAgainst = 0;
        let bestBookieFor = null;
        let bestBookieAgainst = null;
        let timestampFor = null;
        let timestampAgainst = null;
    
        const prices_for = [];
        const prices_against = [];

        // console.log(bookmakersArray)
    
        for (const bookmaker of bookmakersArray) {
            bookmaker.markets.forEach((market) => {
                if (market.key === 'h2h') {
                    market.outcomes.forEach((outcome, index) => {
                        if (index === 0 && outcome.price > bestPriceFor) {
                            bestPriceFor = outcome.price;
                            bestBookieFor = bookmaker.key;
                            timestampFor = market.last_update;
                            prices_for.push(market.outcomes[0].price)
                        }
                        if (index === 1 && outcome.price > bestPriceAgainst) {
                            bestPriceAgainst = outcome.price;
                            bestBookieAgainst = bookmaker.key;
                            timestampAgainst = market.last_update;
                            prices_against.push(market.outcomes[1].price)
                        }
            })}});
        }

        const eventJsonFor = {
            bookie: bestBookieFor,
            type: 'h2h',
            name: 'home',
            price: bestPriceFor,
            number_of_bookies: numberOfBookmakers,
            timestamp: timestampFor,
            // mean_price_for: prices_for.length ? prices_for.reduce((sum, num) => sum + num, 0) / prices_for.length : 0,
            // margin_for: prices_for.length ? ((1 / (prices_for.reduce((sum, num) => sum + num, 0) / prices_for.length) - margin) * bestPriceFor) - 1 : 0
        };
        const eventJsonAgainst = {
            bookie: bestBookieAgainst,
            type: 'h2h',
            name: 'away',
            price: bestPriceAgainst,
            number_of_bookies: numberOfBookmakers,
            timestamp: timestampAgainst,
            // mean_price_against: prices_against.length ? prices_against.reduce((sum, num) => sum + num, 0) / prices_against.length : 0,
            // margin_against: prices_against.length ? ((1 / (prices_against.reduce((sum, num) => sum + num, 0) / prices_against.length) - margin) * bestPriceAgainst) - 1 : 0
        };

        const sum_for = prices_for.reduce((partial_sum, current_num) => partial_sum + current_num, 0)
        const mean_for = sum_for / prices_for.length;
        eventJsonFor['mean_price_for'] = mean_for;

        const sum_against = prices_against.reduce((patrial_sum, current_num) => patrial_sum + current_num, 0)
        const mean_against = sum_against / prices_against.length;
        eventJsonAgainst['mean_price_against'] = mean_against;
    
        console.log(eventJsonFor);
        console.log(eventJsonAgainst);
    };
};

export default {
    processFileContents
};