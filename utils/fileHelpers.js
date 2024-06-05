import fs from 'fs';
import path from 'path';
import config from '../config.js';
import {parse} from 'csv-parse';
import { CsvStringifier } from 'csv-writer/src/lib/csv-stringifiers/abstract.js';

const createDirectoryIfNotExist = (dir) => {
    if (fs.existsSync(dir)) {
        console.log('Dir already exists')
        return true;
    } else {
        // This is currently causing problems
        console.log(`creating Directory: ${dir}`)
        fs.mkdirSync(dir, {recursive: true})
        console.log(`Created Directory: ${dir}`)
    }
};

const doesFileExist = (dir) => {
    if (fs.existsSync(dir)) {
        console.log('File already exists')
        return true;
    } else {
        return false;
    }
};

const returnCsvFiles = (folderPath) => {
    const files = fs.readdirSync(folderPath);
    const csvFiles = files.filter(file => path.extname(file).toLowerCase() === '.csv');
    return csvFiles;
};

// const saveToLegacyDateFolder = () => {
//     // file to save the data in oddsForEvent <- should go at the very very start of client.js

//     // if a file already exists within the oddsForEvent folder with sport name
//     //    read the data from this CSV
//     //    if a file exists within legacyDatasetfolder for certain sport then append to it with CSV contents
//     //    else create file and save data from CSV
//     // else do nothing
//     const oddsCsvFiles = returnCsvFiles(`${config.oddsForEvent.url}`)
//     console.log('=========')
//     console.log(oddsCsvFiles)
//     console.log('=========')
//     for (const sport of oddsCsvFiles) {
//         const legacyDataPath = `${config.legacyDatasetUrl}/${sport}`;
//         const fileExists = doesFileExist(legacyDataPath);
//         if (fileExists) {
//             const path = `${config.oddsForEvent.url}/${sport}`
//             // read the data from the path
//             // append it to the new file at location legacyDataPath
//         } else {
//             // create the file with at location legacyDataPath
//             // add the data to newly created file
//         }
//         console.log('.....')
//         console.log(legacyDataPath)
//         console.log(fileExists)
//         // after data has been saved, delete the file

//     }

// };

const saveToLegacyDateFolder = () => {
    // check if a CSV exists
    // if it does  append to it
    // if not,
    const oddsCsvFiles = returnCsvFiles(config.oddsForEvent.url);

    oddsCsvFiles.forEach(sport => {
        const legacyDataPath = `${config.legacyDatasetUrl}/${sport}`;
        const sportCsvPath = `${config.oddsForEvent.url}/${sport}`;

        //to read the data
        if (doesFileExist(legacyDataPath)) {
            const newData = fs.readFileSync(sportCsvPath, 'utf8');
            console.log()

            parse(newData, {
                columns: true,
                trim: true
            }, (err, output) => {
                if (err) {
                    console.error('Error reading CSV:', err.stack);
                    return;
                }
                const existingData = fs.readFileSync(legacyDataPath, 'utf8');
                const combinedData = [parse(existingData, {columns: true}), ...output];
                const csvString = stringify(combinedData, { header: true });
                fs.writeFileSync(legacyDataPath, csvString, 'utf8');
            });
        } else {
            // it should make the file and write to it
            createDirectoryIfNotExist()
            fs.copyFileSync(sportCsvPath, legacyDataPath);
        }
        
        // console.log('.....');
        // console.log(legacyDataPath);
        // console.log(doesFileExist(legacyDataPath));
        
        // Optionally, delete the original file
        // fs.unlinkSync(sportCsvPath);
    });
};

export default {
    createDirectoryIfNotExist,
    returnCsvFiles,
    saveToLegacyDateFolder
};