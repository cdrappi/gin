import React, { Component } from "react";
import "./Game.css";
import Card from "./Card.js";

class Game extends Component {
  createCard(card, inHand) {
    return (
      <Card
        key={card}
        rank={card[0]}
        suit={card[1]}
        inHand={inHand}
        action={this.props.action}
        game_id={this.props.id}
        refreshGames={this.props.refreshGames}
      />
    );
  }

  render() {
    let html_hand = this.props.hand.map(card => this.createCard(card, true));
    let discard = " ";
    if (this.props.top_of_discard) {
      discard = this.createCard(this.props.top_of_discard, false);
    }

    return (
      <div className={`game ${this.props.action}`}>
        <div className="opponent">
          {" "}
          {this.props.opponent_username}({this.props.id}){" "}
        </div>{" "}
        <div>
          <ul className="hand"> {html_hand} </ul> {" || "}{" "}
          {this.createCard("?x", false)}
          {discard}
        </div>{" "}
      </div>
    );
  }
}

export default Game;
