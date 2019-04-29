import React, { Component } from "react";
import "./Card.css";
import API_HOST from "./api-config";

class Card extends Component {
  constructor(props) {
    super(props);
    let isDummyCard = props.rank === "?" && props.suit === "y";
    let canDraw = props.action === "draw" && !props.inHand && !isDummyCard;
    let canDiscard = props.action === "discard" && props.inHand;
    this.state = {
      isDiscard: !props.inHand && props.rank !== "?",
      canDiscard: canDiscard,
      canDraw: canDraw,
      isClickable: canDraw || canDiscard
    };

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    if (this.state.canDiscard) {
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
    } else if (this.state.canDraw) {
      fetch(`${API_HOST}/dealer/draw/`, {
        method: "POST",
        headers: {
          Authorization: `JWT ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          game_id: this.props.game_id,
          from_discard: this.state.isDiscard
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
    let clickable = this.state.isClickable ? "card-can-click" : "";
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
