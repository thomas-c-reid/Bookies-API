import fileHelpers from '../utils/fileHelpers.js';
import fs from 'fs';
import path from 'path';
import csv from 'csv-parser';


const evaluateBets = () => {
    // For each file in folder data/oddsForEvent that overlap with config.selectedSports
    // for each json in bookmakers
    const filePath = 'data/oddsForEvent';
    const csvFiles = fileHelpers.returnCsvFiles(filePath);
    for (const fileName of csvFiles) {
        console.log(fileName)
        const fileContents = [];
        fs.createReadStream(path.join(filePath, fileName))
          .pipe(csv())  // This ensures csv-parser processes the stream directly
          .on('data', (data) => fileContents.push(data))
          .on('end', () => {
              console.log(`File ${fileName} has been read successfully.`);
              processFileContents(fileContents)
          })
          .on('error', (error) => {
              console.error(`Error reading file ${fileName}:`, error);
          });
    };
};


evaluateBets();
