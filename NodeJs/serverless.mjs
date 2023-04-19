var API_ENDPOINT = 'https://sxmz4whd3h.execute-api.us-east-1.amazonaws.com/dev/gohighlevel';

function sendData (e, pref) {
    fetch(API_ENDPOINT, {
        headers:{
            "Content-type": "application/json"
        },
        method: 'POST',
        body: JSON.stringify({
            type: 'ContactCreate',
            locationId: 'locacion123',
            id: 'id12345',
            email: 'mail@example.com',
            country: 'US',
            firstName: 'John',
            lastName: 'Testoff'
        }),
        mode: 'cors'
    })
    .then((resp) => resp.json())
    .then(function(data) {
        console.log(data)
    })
    .catch(function(err) {
        console.log(err)
    });
};
