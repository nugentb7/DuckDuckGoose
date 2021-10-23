import React from 'react';
import { ViewRect } from '../types/ViewRect';

interface ComponentState {
    view: ViewRect;
    pan?: {
        dx: number;
        dy: number;
    };
}
type ComponentProps = {
    labels?: {
        x: string;
        y: string;
    };
    axisLines?: {
        x?: number;
        y?: number;
    };
};

export class Plot extends React.Component<ComponentProps, ComponentState> {
    protected viewboxRef: React.RefObject<SVGSVGElement>;

    /**
     * Current width of the viewbox, calculated from bounds.
     * @protected
     */
    public get width(): number {
        return this.state.view.y - this.state.view.x;
    }

    /**
     * Current height of the viewbox, calculated from bounds.
     * @protected
     */
    public get height(): number {
        return this.state.view.h - this.state.view.w;
    }

    public constructor(props: ComponentProps) {
        super(props);

        this.viewboxRef = React.createRef();

        this.state = {
            view: {
                x: 0,
                y: 0,
                w: 200,
                h: 100,
            },
        };
    }

    protected onPointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
        const x = event.clientX;
        const y = event.clientY;

        this.setState({
            ...this.state,
            pan: {
                dx: x,
                dy: y,
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
            const panFactor = (200 / this.state.view.w) * 5;
            const x = this.state.view.x + (this.state.pan.dx - event.clientX) / panFactor;
            const y = this.state.view.y + (this.state.pan.dy - event.clientY) / panFactor;

            this.setState({
                view: {
                    ...this.state.view,
                    x: x,
                    y: y,
                },
                pan: {
                    dx: event.clientX,
                    dy: event.clientY,
                },
            });
        }
    };

    protected onWheel = (event: React.WheelEvent<SVGSVGElement>) => {
        event.stopPropagation();

        let { w, h } = this.state.view;
        let amount = event.deltaY / 1000;

        this.setState({
            view: {
                ...this.state.view,
                w: w + w * amount,
                h: h + h * amount,
            },
        });
    };

    protected renderAxisLines() {
        // TODO: Fix incorrect line drawing on odd aspect ratios.
        //  Need to somehow read the width of the element and convert it to SVG units.
        let { x, y, w, h } = this.state.view;

        // desired increments for the lines
        const lrd = this.props.axisLines?.x; // left to right delta
        const tbd = this.props.axisLines?.y; // top to bottom delta

        let key: number = 0;
        const elements: JSX.Element[] = [];

        if (lrd) {
            let rx = Math.floor(y / lrd) * lrd;
            for (let dx = rx; dx < y + h; dx += lrd) {
                elements.push(
                    <line
                        key={`axline-${key++}`}
                        x1={x}
                        y1={dx}
                        x2={x + w}
                        y2={dx}
                        stroke={'black'}
                        strokeWidth={0.25}
                        opacity={0.25}
                    />
                );
                elements.push(
                    <text
                        key={`axline-text-${key++}`}
                        x={x}
                        y={dx}
                        fontSize={3}
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                    >
                        {dx.toFixed(2)}
                    </text>
                );
            }
        }

        if (tbd) {
            let ry = Math.floor(x / tbd) * tbd;
            for (let dy = ry; dy < x + w; dy += tbd) {
                elements.push(
                    <line
                        key={`axline-${key++}`}
                        x1={dy}
                        y1={y}
                        x2={dy}
                        y2={y + h}
                        stroke={'black'}
                        strokeWidth={0.25}
                        opacity={0.25}
                    />
                );
                elements.push(
                    <text
                        key={`axline-text-${key++}`}
                        x={dy}
                        y={y + h}
                        fontSize={3}
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                    >
                        {dy.toFixed(2)}
                    </text>
                );
            }
        }

        return elements;
    }

    public componentDidMount() {
        const bounds = this.viewboxRef.current?.getBoundingClientRect();
        if (bounds) {
            this.setState({
                ...this.state,
                view: {
                    ...this.state.view,
                    w: bounds.width / 4,
                    h: bounds.height / 4,
                },
            });
        }
    }

    render() {
        const { x, w, y, h } = this.state.view;

        return (
            <svg
                width={'100%'}
                height={'400px'}
                viewBox={`${x} ${y} ${w} ${h}`}
                ref={this.viewboxRef}
                style={{ border: '2px solid black' }}
                onPointerDown={this.onPointerDown}
                onPointerUp={this.onPointerUp}
                onPointerMove={this.onPointerMove}
                onWheel={this.onWheel}
            >
                {this.renderAxisLines()}
                {this.props.children}
            </svg>
        );
    }
}
