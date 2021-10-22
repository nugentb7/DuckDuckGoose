import { Container } from 'react-bootstrap';
import { AppDispatch, RootState } from '../store';
import { connect } from 'react-redux';
import React, { SyntheticEvent } from 'react';
import { UUID } from '../util/UUID';
import { Circle } from './Circle';
import CardHeader from 'react-bootstrap/CardHeader';
import * as d3 from 'd3';
import { Reading } from '../store/reading';
import { Bounds } from '../util/Bounds';

const mapStateToProps = (state: RootState) => ({
    data: state.readings.entities,
});
const mapDispatchToProps = (dispatch: AppDispatch) => ({});

interface ComponentState {
    bounds: Bounds;
    pan?: {
        sX: number;
        sY: number;
    };
}
type ComponentProps = ReturnType<typeof mapStateToProps> & ReturnType<typeof mapDispatchToProps>;

class _Graph extends React.Component<ComponentProps, ComponentState> {
    protected ref: React.RefObject<SVGSVGElement>;
    private _id: string | undefined;

    /**
     * Id for this graph, used with D3 to select elements. Not guaranteed to remain constant between redraws, only use locally.
     * @protected
     */
    protected get id(): string {
        if (this._id === undefined) {
            this._id = UUID.generate();
        }
        return this._id;
    }

    /**
     * Current width of the viewbox, calculated from bounds.
     * @protected
     */
    protected get viewWidth(): number {
        return this.state.bounds.max_x - this.state.bounds.min_x;
    }

    /**
     * Current height of the viewbox, calculated from bounds.
     * @protected
     */
    protected get viewHeight(): number {
        return this.state.bounds.max_y - this.state.bounds.min_y;
    }

    public constructor(props: ComponentProps) {
        super(props);

        this.ref = React.createRef();

        this.state = {
            bounds: {
                min_x: 0,
                max_x: 100,
                min_y: -10,
                max_y: 10,
            },
        };
    }

    protected onPointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
        const x = event.clientX;
        const y = event.clientY;

        this.setState({
            ...this.state,
            pan: {
                sX: x,
                sY: y,
            },
        });
    };

    protected onPointerUp = (event: React.PointerEvent<SVGSVGElement>) => {
        this.setState({
            ...this.state,
            pan: undefined,
        });
    };

    protected onPointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
        if (this.state.pan) {
            const panFactor = 5;
            const nX = this.state.bounds.min_x + (this.state.pan.sX - event.clientX) / panFactor;
            const nY = this.state.bounds.min_y + (this.state.pan.sY - event.clientY) / panFactor;

            console.log([nX, nY, nX + this.viewWidth, nY + this.viewHeight]);

            this.setState({
                bounds: {
                    ...this.state.bounds,
                    min_x: nX,
                    max_x: nX + this.viewWidth,
                    min_y: nY,
                    max_y: nY + this.viewHeight,
                },
                pan: {
                    sX: event.clientX,
                    sY: event.clientY,
                },
            });
        }
    };

    protected useEffect() {
        const viewBox = d3.select(this.ref.current);

        viewBox
            .selectAll('circle')
            .data(this.props.data)
            .join(
                (enter) =>
                    enter
                        .append('circle')
                        .attr('cx', ([id, item]) => item.value / 2)
                        .attr('cy', ([id, item]) => item.value / 2)
                        .attr('r', 0)
                        .attr('fill', 'cornflowerblue')
                        .call((enter) =>
                            enter.transition().duration(1200).attr('cy', 10).attr('r', 6).style('opacity', 1)
                        ),
                (update) => update.attr('fill', 'lightgrey'),
                (exit) =>
                    exit
                        .attr('fill', 'tomato')
                        .call((exit) => exit.transition().duration(1200).attr('r', 0).style('opacity', 0).remove())
            );
    }

    render() {
        if (this.props.data === undefined) {
            return 'Loading...';
        }

        const { min_x, min_y, max_x, max_y } = this.state.bounds;

        return (
            <Container fluid id={this.id}>
                <CardHeader>Title should be here</CardHeader>
                <svg
                    viewBox={`${min_x} ${min_y} ${max_x - min_x} ${max_y - min_y}`}
                    ref={this.ref}
                    style={{ border: '2px solid black' }}
                    onPointerDown={this.onPointerDown}
                    onPointerUp={this.onPointerUp}
                    onPointerMove={this.onPointerMove}
                >
                    {Object.values(this.props.data).map((item: Reading, index) => (
                        <Circle key={item.id} x={index * 3} y={item.value} radius={1} />
                    ))}
                </svg>
            </Container>
        );
    }

    protected redraw() {}
}

export const Graph = connect(mapStateToProps, mapDispatchToProps)(_Graph);
