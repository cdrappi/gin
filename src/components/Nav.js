import React from "react";
import PropTypes from "prop-types";
import "./Nav.css";

function Nav(props) {
  const logged_out_nav = (
    <div className="nav">
      <ul>
        <li onClick={() => props.display_form("login")}>LOGIN</li>
        <li onClick={() => props.display_form("signup")}>SIGNUP</li>
      </ul>
    </div>
  );

  const logged_in_nav = (
    <div className="nav">
      <ul>
        <li onClick={props.handle_logout}>LOGOUT</li>
      </ul>
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
