import React from "react";
import PropTypes from "prop-types";
import "./Nav.css";

function Nav(props) {
  const logged_out_nav = (
    <div className="nav">
      <button
        className="nav-button"
        onClick={() => props.display_form("login")}
      >
        LOGIN
      </button>
      <button
        className="nav-button"
        onClick={() => props.display_form("signup")}
      >
        SIGNUP
      </button>
    </div>
  );

  const logged_in_nav = (
    <div className="nav">
      <button className="nav-button" onClick={props.handle_logout}>
        LOGOUT
      </button>
    </div>
  );
  return <div>{props.logged_in ? logged_in_nav : logged_out_nav}</div>;
}

export default Nav;

Nav.propTypes = {
  logged_in: PropTypes.bool.isRequired,
  display_form: PropTypes.func.isRequired,
  handle_logout: PropTypes.func.isRequired
};
