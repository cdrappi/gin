let API_HOST;

const hostname = window && window.location && window.location.hostname;

if (hostname === "heyhowsgame.herokuapp.com") {
  API_HOST = "https://heyhowsgame.herokuapp.com";
} else {
  API_HOST = "http://127.0.0.1:8000";
}

// for using local npm to ping heroku server
// API_HOST = "https://heyhowsgame.herokuapp.com";

export default API_HOST;
