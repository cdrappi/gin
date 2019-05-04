import React, { Component } from "react";
import "./GameSeries.css";

class GameSeries extends Component {
  constructor(props) {
    super(props);
    this.state = {
      won: props.opponent_points - props.points > 0
    };
  }

  formatDollars(dollars) {
    let rounded_dollars = Math.abs(dollars).toFixed(2);
    if (dollars >= 0) {
      return "$" + rounded_dollars;
    } else {
      return "-$" + rounded_dollars;
    }
  }

  render() {
    let points_margin = this.props.opponent_points - this.props.points;
    let cssClass = points_margin > 0 ? "final-score-win" : "final-score-loss";
    let pointsText = this.props.points + "-" + this.props.opponent_points;

    let dollars = (points_margin * this.props.cents_per_point) / 100;

    return (
      <div className="game-series">
        <div>
          {" "}
          {this.props.opponent_username}({this.props.id}){" "}
          <div>
            <span className={`final-score`}>{pointsText}</span>
            {" | "}
            <span className={`final-score ${cssClass}`}>
              {this.formatDollars(dollars)}
            </span>
            <div>
              {this.props.concurrent_games} MG | {this.props.points_to_stop} PS
              | {this.props.complete_games}/{this.props.incomplete_games} games
              | ${this.props.cents_per_point / 100}/pt
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default GameSeries;
