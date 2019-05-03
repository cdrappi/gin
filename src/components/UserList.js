import React, { Component } from "react";
import "./UserList.css";
import API_HOST from "./api-config";

class UserList extends Component {
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

    this.handleOpponentChange = this.handleOpponentChange.bind(this);
    this.handlePointsChange = this.handlePointsChange.bind(this);
    this.handleGamesChange = this.handleGamesChange.bind(this);
    this.handleCentsChange = this.handleCentsChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleOpponentChange(event) {
    this.setState({ opponent_id: event.target.value });
  }

  handlePointsChange(event) {
    this.setState({ points_to_stop: event.target.value });
  }

  handleGamesChange(event) {
    this.setState({ concurrent_games: event.target.value });
  }

  handleCentsChange(event) {
    this.setState({ cents_per_point: event.target.value });
  }

  handleSubmit() {
    if (this.state.opponent_id === -1) {
      alert("Please select an opponent");
      return;
    }
    if (this.state.isLoggedIn) {
      fetch(`${API_HOST}/dealer/users/`, {
        method: "POST",
        headers: {
          Authorization: `JWT ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          opponent_id: this.state.opponent_id,
          points_to_stop: this.state.points_to_stop,
          concurrent_games: this.state.concurrent_games,
          cents_per_point: this.state.cents_per_point
        })
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
        window.location.reload();
      }
    }
  }
  render() {
    let options = [
      <option key={-1} value={-1}>
        SELECT
      </option>
    ];
    try {
      let actual_options = this.state.users.map(u => (
        <option key={u.id} value={u.id}>
          {u.username} ({u.id})
        </option>
      ));
      options = options.concat(actual_options);
    } catch {
      localStorage.removeItem("token");
      window.location.reload();
    }

    return (
      <div>
        <h2>Create a new game</h2>
        <form onSubmit={this.handleSubmit}>
          <div>
            <label>
              Username:
              <select
                value={this.state.opponent_id}
                onChange={this.handleOpponentChange}
              >
                {options}
              </select>
            </label>
          </div>
          <div>
            <label>
              Points to stop
              <input
                type="text"
                pattern="[0-9]*"
                onChange={this.handlePointsChange}
                value={this.state.points_to_stop}
              />
            </label>
          </div>
          <div>
            <label>
              Concurrent games
              <input
                type="text"
                pattern="[0-9]*"
                onChange={this.handleGamesChange}
                value={this.state.concurrent_games}
              />
            </label>
            <input type="submit" value="Create" />
          </div>
          <div>
            <label>
              Cents per point
              <input
                type="text"
                pattern="[0-9]*"
                onChange={this.handleCentsChange}
                value={this.state.cents_per_point}
              />
            </label>
            <input type="submit" value="Create" />
          </div>
        </form>
      </div>
    );
  }
}

export default UserList;
