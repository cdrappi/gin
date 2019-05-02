import React, { Component } from "react";
import "./Card.css";
import API_HOST from "./api-config";

class Card extends Component {
  constructor(props) {
    super(props);
    this.state = {};

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  isDiscard = () => !this.props.inHand && this.props.rank !== "?";
  isDummyCard = () => this.props.rank === "?" && this.props.suit === "y";
  canDiscard = () => this.props.action === "discard" && this.props.inHand;
  canDraw() {
    return (
      this.props.action === "draw" &&
      !this.props.inHand &&
      !this.props.is_last_draw
    );
  }

  isClickable = () => this.canDiscard() || this.canDraw();

  handleClick() {
    if (this.canDiscard()) {
      let card = this.props.rank + this.props.suit;
      fetch(`${API_HOST}/dealer/discard/`, {
        method: "POST",
        headers: {
          Authorization: `JWT ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          game_id: this.props.game_id,
          card: card
        })
      })
        .then(res => res.json())
        .then(json => {
          this.props.refreshGames();
        });
    } else if (this.canDraw()) {
      fetch(`${API_HOST}/dealer/draw/`, {
        method: "POST",
        headers: {
          Authorization: `JWT ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          game_id: this.props.game_id,
          from_discard: this.isDiscard()
        })
      })
        .then(res => res.json())
        .then(json => {
          this.props.refreshGames();
        });
    }
  }

  render() {
    let lastDrawn = this.props.is_last_drawn ? "card-last-drawn" : "";
    let clickable = this.isClickable() ? "card-can-click" : "";
    return (
      <span>
        <button
          key={`${this.props.suit}${this.props.rank}`}
          className={`card card-${this.props.suit} ${lastDrawn} ${clickable}`}
          onClick={this.handleClick}
        >
          {this.props.rank}{" "}
        </button>{" "}
      </span>
    );
  }
}

export default Card;
