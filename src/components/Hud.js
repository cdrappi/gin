import React, { Component } from "react";
import "./Hud.css";

const ranks = "A23456789TJQK".split("");
const suits = "cdhs".split("");
const suit_emojis = {
  c: "♣️",
  d: "♦️",
  h: "♥️",
  s: "♠️"
};
const location_css_map = {
  u: "hud-users-hand",
  o: "hud-opponents-hand",
  d: "hud-discard",
  t: "hud-top-of-discard",
  undefined: "unknown"
  // TODO: opponents-last-drawn
};

class Hud extends Component {
  suitHeader(suit) {
    return (
      <th key={suit} className={`header-${suit}`}>
        {suit_emojis[suit]}
      </th>
    );
  }

  tableData(card) {
    // let rank = card[0];
    // let suit = card[1];
    let loc = this.props.hud[card];
    let locCss = location_css_map[loc];
    return <td key={card} className={`${locCss}`} />;
  }
  mapSuitData(i) {
    // returns a function that maps suit to their table data
    return s => this.tableData(ranks[i] + s);
  }

  render() {
    let tableHeader = [<th key="h0" />].concat(
      suits.map(s => this.suitHeader(s))
    );
    let tableData = [];
    for (var i = 0; i < ranks.length; i++) {
      tableData.push(
        <tr key={`r${i + 1}`}>
          <td key={ranks[i]}>{ranks[i]}</td>
          {suits.map(this.mapSuitData(i))}
        </tr>
      );
    }

    return (
      <table className="hud-table">
        <thead className="hud-header">
          <tr key="r0">{tableHeader}</tr>
        </thead>
        <tbody className="hud-body">{tableData}</tbody>
      </table>
    );
  }
}

export default Hud;
