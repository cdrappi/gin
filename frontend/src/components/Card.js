import React, { Component } from "react";
import "./Card.css";

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
    console.log(this.state);
    if (this.props.action === "discard" && this.props.inHand) {
      let card = this.props.rank + this.props.suit;
      fetch("http://localhost:8000/dealer/discard/", {
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
      fetch("http://localhost:8000/dealer/draw/", {
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
    return (
      <span>
        <li
          key={`${this.props.suit}${this.props.rank}`}
          className={`card card-${this.props.suit}`}
          onClick={this.handleClick}
        >
          {this.props.rank}{" "}
        </li>{" "}
      </span>
    );
  }
}

export default Card;
