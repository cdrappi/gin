import React, { Component } from "react";
import "./Game.css";

class CompleteGame extends Component {
  constructor(props) {
    super(props);
    let pointsDiff = props.opponent_points - props.points;
    this.state = {
      pointsDiff: Math.abs(pointsDiff),
      won: pointsDiff > 0
    };
  }
  render() {
    let cssClass = this.state.won ? "final-score-win" : "final-score-loss";
    let pointsText = (this.state.won ? "+" : "-") + this.state.pointsDiff;

    return (
      <div className="game">
        <div className="opponent">
          {" "}
          {this.props.opponent_username}({this.props.id}){" "}
          <span className={`final-score ${cssClass}`}>{pointsText}</span>
        </div>
      </div>
    );
  }
}

export default CompleteGame;
