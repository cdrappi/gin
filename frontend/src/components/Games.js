import React, { Component } from "react";
import "./Games.css";
import Game from "./Game";

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

  newGame(g) {
    return (
      <Game
        key={g.id.toString()}
        id={g.id}
        action={g.action}
        opponent_username={g.opponent_username}
        hand={g.hand}
        top_of_discard={g.top_of_discard}
      />
    );
  }

  render() {
    let draw_games = this.state.draw.map(g => this.newGame(g));
    let discard_games = this.state.discard.map(g => this.newGame(g));
    let wait_games = this.state.wait.map(g => this.newGame(g)); // [<Game />]; //
    return (
      <div>
        <h2>ALL GAMES</h2>
        <div>
          <h3>YOUR DRAW</h3>
          {draw_games}
          <h3>YOUR DISCARD</h3>
          {discard_games}
          <h3>OPPONENT ACTS</h3>
          {wait_games}
        </div>
      </div>
    );
  }
}

export default Games;
