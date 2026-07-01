
const https = require('https');
const cheerio = require("cheerio");

var url = "https://gaswizard.ca/gas-price-predictions/"

function main(city) {
    var date_string, price, direction, amount;
    https.get(url, res => {
        res.setEncoding("utf8");
        let body = "";
        res.on("data", data => {
            body += data;
        });

        res.on("end", () => {
            // console.log(body);
            var $ = cheerio.load(body);
            var cityInfo = cheerio.load($(`td:contains("${city}")`).parent().html(), null, false)('td')

            date_string = $('.price-date').text()
            price = cityInfo.next().html().split(/<|>/)[0].trim()
            amount = cityInfo.next().html().split(/<|>/)[2].trim()

            // Get Price Direction
            if (cityInfo.next().html().includes("pd-up")) {
                direction = 'go UP'
            } else if (cityInfo.next().html().includes("pd-nc")) {
                direction = "NOT CHANGE"
            } else if (cityInfo.next().html().includes("pd-down")) {
                direction = "go DOWN"
            }
            
            let message = date_string
            if (direction === "NOT CHANGE") {
                message = message + "\nGas will NOT CHANGE and stay at " + price + "¢/L"
                console.log(message);
            } else {
                message = message + "\nGas will " + direction + " by " + amount + "¢ to " + price + "¢/L"
                console.log(message);
            };
        });
    });
}

main("Toronto");