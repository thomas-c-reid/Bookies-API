import { Parser } from 'json2csv';
import { writeFileSync } from 'fs';


const csvSave = (data, filename, fieldMapping) => {   
    
    const opts = { fieldMapping };
    const parser = new Parser(opts);
    const csv = parser.parse(data);

    writeFileSync(filename, csv);
};

export default {
    csvSave
}