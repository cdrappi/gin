import React, { Component } from "react";
import "./Games.css";

class Games extends Component {
  constructor(props) {
    super(props);
    this.state = {
      draw: [],
      discard: [],
      wait: []
    };
    this.refreshGames();
  }

  refreshGames() {
    fetch("http://localhost:8000/dealer/games/", {
      headers: {
        Authorization: `JWT ${localStorage.getItem("token")}`
      }
    })
      .then(res => res.json())
      .then(json => {
        this.setState({
          draw: json.draw,
          discard: json.discard,
          wait: json.wait
        });
      });
  }

  render() {
    let draw_games = this.state.draw; // [<div>{"value"}</div>];
    let discard_games = [<div>{"value"}</div>];
    let wait_games = [<div>{"value"}</div>];

    return (
      <div>
        <h3>YOUR DRAW</h3>
        {draw_games}
        <h3>YOUR DISCARD</h3>
        {discard_games}
        <h3>OPPONENT ACTS</h3>
        {wait_games}
      </div>
    );
  }
}

export default Games;
