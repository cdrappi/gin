import React, { Component } from "react";
import Login from "./components/Login";
// import Games from "./components/Games";
// import UserList from "./components/UserList";
import "./App.css";

class App extends Component {
  render() {
    return (
      <div>
        <Login />
        {/* <Games /> */}
        {/* <UserList /> */}
      </div>
    );
  }
}

export default App;
