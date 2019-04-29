import React, { Component } from "react";
import "./Card.css";
import API_HOST from "./api-config";

class Card extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isDiscard: !props.inHand && props.rank !== "?",
      isDeck: !props.inHand && props.rank === "?"
    };

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    if (this.props.action === "discard" && this.props.inHand) {
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
    } else if (this.props.action === "draw" && !this.props.inHand) {
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
    let cssIsLastDrawn = this.props.is_last_drawn ? "card-last-drawn" : "";
    return (
      <span>
        <li>
          <button
            key={`${this.props.suit}${this.props.rank}`}
            className={`card card-${this.props.suit} ${cssIsLastDrawn}`}
            onClick={this.handleClick}
          >
            {this.props.rank}{" "}
          </button>
        </li>{" "}
      </span>
    );
  }
}

export default Card;
