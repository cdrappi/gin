import React, { Component } from "react";
import Login from "./components/Login";
import Games from "./components/Games";
import "./App.css";

class App extends Component {
  render() {
    return (
      <div>
        <Login />
        <Games />
      </div>
    );
  }
}

export default App;
