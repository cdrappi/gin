import React, { Component } from "react";
import "./User.css";

class User extends Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.challengeUser = this.challengeUser.bind(this);
  }

  challengeUser(user_id) {
    fetch("http://localhost:8000/dealer/create/", {
      method: "POST",
      headers: {
        Authorization: `JWT ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({
        opponent_id: this.props.id
      })
    }).then(res => window.location.reload());
  }

  render() {
    return (
      <div>
        <button onClick={this.challengeUser}>
          {this.props.username} ({this.props.id})
        </button>
      </div>
    );
  }
}

export default User;
