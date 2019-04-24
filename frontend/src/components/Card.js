import React, { Component } from "react";
import "./Card.css";

class Card extends Component {
  constructor(props) {
    super(props);

    let canDiscard = props.action === "discard" && props.inHand;
    let canDraw = props.action === "draw" && props.isDiscard;
    this.state = {
      clickable: canDiscard || canDraw
    };

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    if (this.state.clickable) {
      // TODO: post message
      if (this.props.action == "discard") {
        // TODO: post to /discard
        console.log("discarding " + this.props.rank + this.props.suit);
      } else if (this.props.action == "draw") {
        // TODO: post to /draw from discard
        console.log(
          "drawing from discard " + this.props.rank + this.props.suit
        );
      }
    }
  }

  render() {
    return (
      <div>
        <li
          key={`${this.props.suit}${this.props.rank}`}
          className={`card card-${this.props.suit}`}
          onClick={this.handleClick()}
        >
          {this.props.rank}{" "}
        </li>{" "}
      </div>
    );
  }
}

export default Card;
