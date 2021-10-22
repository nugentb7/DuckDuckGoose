import { Container } from 'react-bootstrap';
import { AppDispatch, RootState } from '../store';
import { connect } from 'react-redux';
import React, { SyntheticEvent } from 'react';
import CardHeader from 'react-bootstrap/CardHeader';
import { Reading } from '../store/reading';
import { Plot } from './Plot';

const mapStateToProps = (state: RootState) => ({
    data: state.readings.entities,
});
const mapDispatchToProps = (dispatch: AppDispatch) => ({});

interface ComponentState {}
type ComponentProps = ReturnType<typeof mapStateToProps> & ReturnType<typeof mapDispatchToProps>;

class _Graph extends React.Component<ComponentProps, ComponentState> {
    public constructor(props: ComponentProps) {
        super(props);
    }

    render() {
        if (this.props.data === undefined) {
            return 'Loading...';
        }

        const graphLines: JSX.Element[] = [];
        const data: Reading[] = Object.values(this.props.data);

        for (let i = 1; i < data.length; i++) {
            graphLines.push(
                <line
                    key={`line-${data[i].id}`}
                    x1={i - 1}
                    y1={data[i - 1].value}
                    x2={i}
                    y2={data[i].value}
                    stroke={'rgba(0,0,0,1)'}
                    strokeWidth={0.25}
                />
            );
        }

        return (
            <Container fluid>
                <CardHeader>Title should be here</CardHeader>
                <Plot axisLines={{ x: 10, y: 10 }}>
                    {graphLines}
                    {Object.values(this.props.data).map((item: Reading, index) => (
                        <circle key={`dot-${item.id}`} cx={index} cy={item.value} r={0.5} />
                    ))}
                </Plot>
            </Container>
        );
    }
}

export const Graph = connect(mapStateToProps, mapDispatchToProps)(_Graph);
