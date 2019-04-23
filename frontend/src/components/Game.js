import React from "react";
import "./Game.css";

function Game(props) {
  let hand = props.hand.map(card => (
    <li key={card} className={`card card-${card[1]}`}>
      {card}
    </li>
  ));
  return (
    <div className="game">
      Game {props.id} vs. {props.opponent_username} [{props.action}]
      <ul>{hand}</ul>
      Discard:{" "}
      <div className={`card card-${props.top_of_discard[1]}`}>
        {props.top_of_discard}
      </div>
    </div>
  );
}

// {
//       id: props.id,
//       action: props.action,
//       opponent_username: props.opponent_username,
//       hand: props.hand,
//       top_of_discard: props.top_of_discard
//     }

export default Game;
