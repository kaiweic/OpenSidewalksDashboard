import React from "react";
import { apiKey } from "./ApiKey";

export default class LandingPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            soda_api_key: apiKey(),
        }
    }

    handleResponse(response) {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(function (err) {
                throw new Error(err.errorMessage);
            });
        }
    }

    displayData(data) {
        console.log(data);
    }

    handleError(message) {
        alert(message);
    }

    getData(query) {
        fetch(query)
        .then(this.handleResponse)
        .then(this.displayData)
        .catch(this.handleError);
    }

    render() {
        let query = "https://data.seattle.gov/resource/y7pv-r3kh.geojson?$limit=20000&$$app_token=<<api_key>>";
        return(
            <div className="container">
                <h2>Landing Page</h2>
                <button className="btn btn-primary" onClick={evt => this.getData(query.replace("<<api_key>>", this.state.soda_api_key))}>get data</button>
            </div>
        );
    }
}