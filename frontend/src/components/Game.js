import React, { Component } from "react";
import "./Game.css";

class Game extends Component {
  render() {
    let html_hand = this.props.hand.map(card => (
      <li key={card} className={`card card-${card[1]}`}>
        {card[0]}
      </li>
    ));
    return (
      <div className="game">
        <div className="opponent">
          {this.props.opponent_username} ({this.props.id})
        </div>
        <div>
          <ul className="hand">{html_hand}</ul>
          {" || "}
          <span className="card deck">?</span>{" "}
          <span className={`card card-${this.props.top_of_discard[1]}`}>
            {this.props.top_of_discard[0]}
          </span>
        </div>
      </div>
    );
  }
}

// {
//       id: props.id,
//       action: props.action,
//       opponent_username: props.opponent_username,
//       hand: props.hand,
//       top_of_discard: props.top_of_discard
//     }

export default Game;
