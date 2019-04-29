import React, { Component } from "react";
import "./UserList.css";
import User from "./User.js";
import API_HOST from "./api-config";

class UserList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoggedIn: localStorage.getItem("token") ? true : false,
      users: []
    };

    // This binding is necessary to make `this` work in the callback
    this.getUsers();
  }

  createUser(u) {
    return <User key={u.id} id={u.id} username={u.username} />;
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
      }
    }
  }
  render() {
    // TODO: clean this up going forward...
    // no idea of best pattern right now and just wanna play some fucking gin
    let users = [];
    try {
      users = this.state.users.map(u => this.createUser(u));
    } catch {
      localStorage.removeItem("token");
    }
    return (
      <div className="user-list">
        <h2>Create a game</h2>
        <div>{users}</div>
      </div>
    );
  }
}

export default UserList;
