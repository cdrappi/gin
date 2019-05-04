import React, { Component } from "react";
import GameSeries from "./GameSeries";
import API_HOST from "./api-config";
import "./GameSeriesList.css";

class GameSeriesList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      complete: [],
      incomplete: []
    };
    this.refreshGameSeries = this.refreshGameSeries.bind(this);
    this.refreshGameSeries();
  }

  refreshGameSeries() {
    fetch(`${API_HOST}/dealer/game_series/`, {
      headers: {
        Authorization: `JWT ${localStorage.getItem("token")}`
      }
    })
      .then(res => res.json())
      .then(json => {
        this.setState({
          complete: json.complete,
          incomplete: json.incomplete
        });
      });
  }

  newGameSeries(g) {
    return (
      <GameSeries
        key={g.id.toString()}
        id={g.id}
        opponent_id={g.opponent_id}
        opponent_username={g.opponent_username}
        points={g.points}
        opponent_points={g.opponent_points}
        points_to_stop={g.points_to_stop}
        concurrent_games={g.concurrent_games}
        cents_per_point={g.cents_per_point}
        refreshGames={this.refreshGames}
      />
    );
  }

  render() {
    let complete_games = this.state.complete.map(g => this.newGameSeries(g));
    let incomplete_games = this.state.incomplete.map(g =>
      this.newGameSeries(g)
    );
    return (
      <div className="game-series-list">
        <h2>SERIES</h2>
        {"  "}
        <span onClick={this.refreshGameSeries} className="reload">
          &#x21bb;
        </span>
        <div>
          <div>
            <h3>Active</h3>
            {incomplete_games}
          </div>
          <div>
            <h3>Completed</h3>
            {complete_games}
          </div>
        </div>
      </div>
    );
  }
}

export default GameSeriesList;
