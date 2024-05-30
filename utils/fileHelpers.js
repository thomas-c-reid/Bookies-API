import fs from 'fs';

const createDirectoryIfNotExist = (dir) => {
    console.log(dir)
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

export default {
    createDirectoryIfNotExist
};