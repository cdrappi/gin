import React, { Component } from "react";
import Login from "./components/Login";
import Games from "./components/Games";
import CreateGameSeries from "./components/CreateGameSeries";
import "./App.css";

class App extends Component {
  render() {
    return (
      <div>
        <Login />
        <Games />
        <CreateGameSeries />
      </div>
    );
  }
}

export default App;
