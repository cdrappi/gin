import React, { Component } from "react";
import "./Hud.css";

const ranks = "A23456789TJQKA".split("");
const suits = "cdhs".split("");
const suit_emojis = {
  c: "♣️",
  d: "♦️",
  h: "♥️",
  s: "♠️"
};
const location_css_map = {
  u: "users-hand",
  o: "opponents-hand",
  d: "discard",
  t: "top-of-discard"
  // TODO: opponents-last-drawn
};

class Hud extends Component {
  element(card) {
    // let rank = card[0];
    // let suit = card[1];
    let loc = this.props.hud[card];
    let locCss = location_css_map[loc];
    return <div class={`${locCss}`} />;
  }
  render() {
    return <div />;
  }
}

export default Hud;
