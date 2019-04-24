import React, { Component } from "react";
import "./Card.css";

class Card extends Component {
  render() {
    return (
      <div>
        <li
          key={`${this.props.suit}${this.props.rank}`}
          className={`card card-${this.props.suit}`}
        >
          {this.props.rank}{" "}
        </li>{" "}
      </div>
    );
  }
}

export default Card;
