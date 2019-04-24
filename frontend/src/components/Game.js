import React, { Component } from "react";
import "./Game.css";
import Card from "./Card.js";

class Game extends Component {
  createCard(card) {
    return <Card key={card} rank={card[0]} suit={card[1]} />;
  }

  render() {
    let html_hand = this.props.hand.map(card => this.createCard(card));

    return (
      <div className="game">
        <div className="opponent">
          {" "}
          {this.props.opponent_username}({this.props.id}){" "}
        </div>{" "}
        <div>
          <ul className="hand"> {html_hand} </ul> {" || "}{" "}
          <span className="card deck"> ? </span>{" "}
          <span className={`card card-${this.props.top_of_discard[1]}`}>
            {" "}
            {this.props.top_of_discard[0]}{" "}
          </span>{" "}
        </div>{" "}
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
