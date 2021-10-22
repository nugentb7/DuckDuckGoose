import { AppDispatch, RootState } from '../store';
import React from 'react';
import { Col, Container, Row } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Graph } from '../component/Graph';

const mapStateToProps = (state: RootState) => ({});
const mapDispatchToProps = (dispatch: AppDispatch) => ({});

interface ComponentState {}
type ComponentProps = ReturnType<typeof mapStateToProps> & ReturnType<typeof mapDispatchToProps>;

class _Home extends React.Component<ComponentProps, ComponentState> {
    render() {
        return (
            <Container fluid>
                <Row>
                    <Col xs={2}>Sidebar here</Col>
                    <Col>
                        <Graph />
                    </Col>
                </Row>
            </Container>
        );
    }
}

export const Home = connect(mapStateToProps, mapDispatchToProps)(_Home);
