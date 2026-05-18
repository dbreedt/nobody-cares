import http from 'k6/http';
import { check } from 'k6';

// Define the URL
const url = 'http://localhost:8080/user/';

export default function () {
    // Random nr between 1 - 500000
    const turl = url + (Math.floor(Math.random() * 500000) + 1);
    const res = http.get(turl);

    const is200 = check(res, {
        'status is 200': (r) => r.status === 200,
    });

    if (!is200) {
        console.log(`Request failed! ${turl} Status: ${res.status}`);
    }
}

