import { Parser } from 'json2csv';
import { writeFileSync } from 'fs';


const csvSave = (data, filename, fieldMapping) => {    
    if (Array.isArray(data) == false) {
        console.error('Expected an array but got:', typeof data);
    };

    const opts = { fieldMapping };
    const parser = new Parser(opts);
    const csv = parser.parse(data);

    writeFileSync(filename, csv);
    console.log(`Successfully written to ${filename} CSV`);
};

export default {
    csvSave
}