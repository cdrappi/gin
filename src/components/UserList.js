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
    if (this.props.isLoggedIn) {
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
    }
  }
  render() {
    let users = this.state.users.map(u => this.createUser(u));
    return (
      <div>
        <h2>Create a game</h2>
        <div>{users}</div>
      </div>
    );
  }
}

export default UserList;
