import React, { Component } from "react";
import "./CreateGameSeries.css";
import API_HOST from "./api-config";

class CreateGameSeries extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoggedIn: localStorage.getItem("token") ? true : false,
      users: [],
      opponent_id: -1,
      points_to_stop: 0,
      concurrent_games: 1,
      cents_per_point: 0
    };

    // This binding is necessary to make `this` work in the callback
    this.getUsers();

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
  }

  handleSubmit() {
    if (this.state.opponent_id === -1) {
      alert("Please select an opponent");
      return;
    }
    if (this.state.isLoggedIn) {
      let json_body = JSON.stringify({
        opponent_id: parseInt(this.state.opponent_id),
        points_to_stop: parseInt(this.state.points_to_stop),
        concurrent_games: parseInt(this.state.concurrent_games),
        cents_per_point: parseInt(this.state.cents_per_point)
      });

      fetch(`${API_HOST}/dealer/create/`, {
        method: "POST",
        headers: {
          Authorization: `JWT ${localStorage.getItem("token")}`
        },
        body: json_body
      }).then(res => {
        window.location.reload();
      });
    }
  }

  getUsers() {
    if (this.state.isLoggedIn) {
      try {
        fetch(`${API_HOST}/dealer/users/`, {
          method: "GET",
          headers: {
            Authorization: `JWT ${localStorage.getItem("token")}`
          }
        })
          .then(res => res.json())
          .then(json => {
            this.setState({
              users: json
            });
          });
      } catch {
        // assume token is stale, make user login again
        localStorage.removeItem("token");
        // this.setState({ isLoggedIn: false });
        // window.location.reload();
      }
    }
  }
  render() {
    let options = [];
    if (this.state.opponent_id === -1) {
      options = [
        <option key={-1} value={-1}>
          SELECT OPPONENT
        </option>
      ];
    }
    try {
      let actual_options = this.state.users.map(u => (
        <option key={u.id} value={u.id}>
          {u.username} ({u.id})
        </option>
      ));
      options = options.concat(actual_options);
    } catch {
      // TODO: clean up auth, this hack sucks
      localStorage.removeItem("token");
      window.location.reload();
    }
    return (
      <div className="CreateGameSeries">
        <h2>NEW GAME</h2>
        <div className="input-container">
          <div className="input-section">
            <select
              id="opponent_id"
              name="opponent_id"
              value={this.state.opponent_id}
              onChange={this.handleChange}
              className="opponent-selector"
            >
              {options}
            </select>
          </div>
          <div className="input-section">
            <span className="input-description">Points</span>
            <input
              type="text"
              id="points_to_stop"
              name="points_to_stop"
              onChange={this.handleChange}
              value={this.state.points_to_stop}
              className="input-item"
            />
          </div>
          <div className="input-section">
            <span className="input-description">Games</span>
            <input
              type="text"
              id="concurrent_games"
              name="concurrent_games"
              onChange={this.handleChange}
              value={this.state.concurrent_games}
              className="input-item"
            />
          </div>
          <div className="input-section">
            <span className="input-description">Cents/point</span>
            <input
              type="text"
              id="cents_per_point"
              name="cents_per_point"
              onChange={this.handleChange}
              value={this.state.cents_per_point}
              className="input-item"
            />
          </div>
          <div>
            <button onClick={this.handleSubmit} className="create-button">
              CREATE
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export default CreateGameSeries;
