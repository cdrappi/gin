import React, { Component } from "react";
import Nav from "./Nav";
import LoginForm from "./LoginForm";
import SignupForm from "./SignupForm";
import "./Login.css";
import API_HOST from "./api-config";

class Login extends Component {
  constructor(props) {
    super(props);
    this.state = {
      displayed_form: "",
      logged_in: false,
      username: "",
      message: ""
    };
  }

  getToken() {
    return localStorage.getItem("token");
  }

  deleteToken() {
    localStorage.removeItem("token");
  }

  componentDidMount() {
    if (this.getToken()) {
      try {
        fetch(`${API_HOST}/dealer/current_user/`, {
          headers: {
            Authorization: `JWT ${this.getToken()}`
          }
        })
          .then(res => res.json())
          .then(json => {
            this.setState({
              username: json.username,
              logged_in: true
            });
          });
      } catch {
        this.deleteToken();
      }
    }
  }

  handle_login = (e, data) => {
    e.preventDefault();
    fetch(`${API_HOST}/token_auth/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(json => {
        localStorage.setItem("token", json.token);
        this.setState({
          logged_in: true,
          displayed_form: "",
          username: json.user.username,
          message: ""
        });
        window.location.reload();
      })
      .catch(err => {
        this.setState({ message: "failure logging in. try again" });
        this.display_form();
        // throw new Error("invalid login");
      });
  };

  handle_signup = (e, data) => {
    e.preventDefault();
    fetch(`${API_HOST}/dealer/users/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(json => {
        localStorage.setItem("token", json.token);
        this.setState({
          logged_in: true,
          displayed_form: "",
          username: json.username
        });
      });
  };

  handle_logout = () => {
    this.deleteToken();
    this.setState({ logged_in: false, username: "" });
  };

  display_form = form => {
    this.setState({
      displayed_form: form
    });
  };

  render() {
    let form;
    switch (this.state.displayed_form) {
      case "login":
        form = <LoginForm handle_login={this.handle_login} />;
        break;
      case "signup":
        form = <SignupForm handle_signup={this.handle_signup} />;
        break;
      default:
        form = null;
    }

    return (
      <div className="Login">
        <p>{this.state.message}</p>
        <h3 className="greeting">
          {" "}
          {this.state.logged_in
            ? `Logged in as ${this.state.username}`
            : "Please Log In"}{" "}
        </h3>
        <Nav
          logged_in={this.state.logged_in}
          display_form={this.display_form}
          handle_logout={this.handle_logout}
        />{" "}
        {form}
      </div>
    );
  }
}

export default Login;
