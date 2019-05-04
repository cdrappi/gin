import React, { Component } from "react";
import "./Games.css";
import Game from "./Game";
import API_HOST from "./api-config";

const ONE_SECOND = 1000;

class Games extends Component {
  constructor(props) {
    super(props);
    this.state = {
      play: [],
      wait: [],
      complete: []
    };
    this.refreshGames = this.refreshGames.bind(this);
    this.refreshGames();
  }

  componentDidMount() {
    let refreshTime = 1 * ONE_SECOND;
    if (window.location.hostname === "localhost") {
      return;
    }
    setInterval(() => this.refreshGames(), refreshTime);
  }

  refreshGames() {
    fetch(`${API_HOST}/dealer/games/`, {
      headers: {
        Authorization: `JWT ${localStorage.getItem("token")}`
      }
    })
      .then(res => res.json())
      .then(json => {
        this.setState({
          play: json.play,
          wait: json.wait,
          complete: json.complete
        });
      });
  }

  newGame(g) {
    return (
      <Game
        key={g.id.toString()}
        id={g.id}
        series_id={g.series_id}
        action={g.action}
        opponent_username={g.opponent_username}
        hand={g.hand}
        top_of_discard={g.top_of_discard}
        last_draw={g.last_draw}
        deck_length={g.deck_length}
        drawn_card={g.drawn_card}
        hud={g.hud}
        points={g.points}
        refreshGames={this.refreshGames}
      />
    );
  }

  render() {
    let play_games = this.state.play.map(g => this.newGame(g));
    let wait_games = this.state.wait.map(g => this.newGame(g));
    return (
      <div>
        <h2>ALL GAMES</h2>
        {"  "}
        <button onClick={this.refreshGames} className="reload">
          &#x21bb;
        </button>
        <div>
          <div>
            <h3>
              <span className="draw-legend">DRAW</span> OR{" "}
              <span className="discard-legend">DISCARD</span>
            </h3>
            {play_games}
          </div>
          <div>
            <h3>OPPONENT ACTS</h3>
            {wait_games}
          </div>
        </div>
      </div>
    );
  }
}

export default Games;
