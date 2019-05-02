import React, { Component } from "react";
import "./Game.css";
import Card from "./Card.js";

class Game extends Component {
  createCard(card, inHand, isLastDraw) {
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
        is_last_draw={isLastDraw}
      />
    );
  }

  render() {
    let hand_r1 = this.props.hand.slice(0, 4);
    let hand_r2 = this.props.hand.slice(4, this.props.hand.length);

    let cards_r1 = hand_r1.map(c => this.createCard(c, true, false));
    let cards_r2 = hand_r2.map(c => this.createCard(c, true, false));

    let discard = " ";
    if (this.props.top_of_discard) {
      discard = this.createCard(this.props.top_of_discard, false, false);
    }

    let last_draw = " ";
    if (this.props.last_draw) {
      last_draw = this.createCard(this.props.last_draw, false, true);
    }

    return (
      <div className={`game ${this.props.action}`}>
        <div className="game-info">
          <span className="opponent">{this.props.opponent_username}</span> (
          {this.props.deck_length}
          {"/52"})<span className="points">{this.props.points} pts</span>{" "}
        </div>
        <div className="game-cards">
          <div className="hand"> {cards_r1} </div>
          <div className="draw-discard-card">
            {this.createCard("?x", false)}
          </div>
          <div className="last-drawn-card"> </div>
          <div className="hand"> {cards_r2} </div>
          <div className="draw-discard-card">{discard}</div>
          <div className="last-drawn-card">{last_draw}</div>
        </div>
      </div>
    );
  }
}

export default Game;
