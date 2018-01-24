import React, { Component } from 'react';
import { HashRouter as Router, Switch, Redirect, Route } from 'react-router-dom';
import constants from "./Components/Constants";
import LandingPage from "./Components/LandingPage";

class App extends Component {
  render() {
    return (
      <div>
        <Router>
          <Switch>
            <Route exact path={constants.routes.home} component={LandingPage} />
          </Switch>
        </Router>
      </div>
    );
  }
}

export default App;
