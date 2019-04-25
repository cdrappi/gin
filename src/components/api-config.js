let backendHost;

const hostname = window && window.location && window.location.hostname;

if (hostname === "heyhowsgame.herokuapp.com") {
  backendHost = "https://heyhowsgame.herokuapp.com";
} else {
  backendHost = "http://localhost:8080";
}

export const API_HOST = `${backendHost}`;
