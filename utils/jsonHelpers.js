const extractKeyFromSportsArray = (jsonArray) => {
    return jsonArray.map(item => item.key)
}

// This func should maybe be in an file for 'arrayHelpers.js'
const findIntersection = (array1, array2) => {
    return array1.filter(item => array2.includes(item))
}

export default {
    extractKeyFromSportsArray,
    findIntersection
}