import React, { Component } from "react";
import Login from "./components/Login";
import Games from "./components/Games";
import GameSeriesList from "./components/GameSeriesList";
import CreateGameSeries from "./components/CreateGameSeries";
import "./App.css";

class App extends Component {
  render() {
    return (
      <div>
        <Login />
        <Games />
        <GameSeriesList />
        <CreateGameSeries />
      </div>
    );
  }
}

export default App;
