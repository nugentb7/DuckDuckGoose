import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import { applyMiddleware, createStore, compose } from "redux";
import thunkMiddleware from "redux-thunk";
import loggerMiddleware from "redux-logger";
import { Provider } from "react-redux";
import { rootReducer } from "./store";
import { BrowserRouter as Router } from "react-router-dom";
import { apiMiddleware } from "./store/api";
import "bootstrap/dist/css/bootstrap.min.css";

const composeEnhancers =
  (window as any).__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
export const store = createStore(
  rootReducer,
  composeEnhancers(
    applyMiddleware(thunkMiddleware, apiMiddleware, loggerMiddleware)
  )
  // composeEnhancers(applyMiddleware(thunkMiddleware, apiMiddleware))
);

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <Router>
        <App />
      </Router>
    </Provider>
  </React.StrictMode>,
  document.getElementById("root")
);
