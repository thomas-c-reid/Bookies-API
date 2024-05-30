import { Parser } from 'json2csv';
import { writeFileSync } from 'fs';


const csvSave = (data, filename, fieldMapping) => {
    console.log('Type of response.data:', typeof data);
    
    // This can probs go after testing
    if (Array.isArray(data)) {
        console.log('Extracted array:', typeof data);
    } else {
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