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
        is_last_drawn={card === this.props.drawn_card}
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

    let last_draw = " ";
    if (this.props.last_draw) {
      last_draw = this.createCard(this.props.last_draw, false);
    }

    return (
      <div className={`game ${this.props.action}`}>
        <div className="game-info">
          <span className="opponent">{this.props.opponent_username}</span> (
          {this.props.deck_length}
          {"/52"})<span class="points">{this.props.points} pts</span>{" "}
        </div>
        <div>
          <ul className="hand"> {html_hand} </ul> {" || "}{" "}
          {this.createCard("?x", false)}
          {discard}
          <span>
            {this.props.last_draw ? " | " : ""}
            {last_draw}
          </span>
        </div>{" "}
      </div>
    );
  }
}

export default Game;
