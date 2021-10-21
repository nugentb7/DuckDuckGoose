import React from "react";
import { Container } from "react-bootstrap";
import { AppDispatch, RootState } from "./store";
import { connect } from "react-redux";
import { requestReadings } from "./store/reading/actions";

const mapStateToProps = (state: RootState) => ({});
const mapDispatchToProps = (dispatch: AppDispatch) => ({
  requestReadings: () => dispatch(requestReadings()),
});

type RootAppProps = ReturnType<typeof mapStateToProps> &
  ReturnType<typeof mapDispatchToProps>;

class RootApp extends React.Component<any, any> {
  render() {
    return <Container>Hello World!</Container>;
  }
}

export const App = connect(mapStateToProps, mapDispatchToProps)(RootApp);
