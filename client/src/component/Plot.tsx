import React from 'react';

interface ComponentState {
    view: {
        x: number;
        y: number;
        zoom: number;
    };
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
    zoom?: {
        max?: number;
        min?: number;
    };
};

export class Plot extends React.Component<ComponentProps, ComponentState> {
    protected viewboxRef: React.RefObject<SVGSVGElement>;

    public constructor(props: ComponentProps) {
        super(props);

        this.viewboxRef = React.createRef();

        this.state = {
            view: {
                x: 0,
                y: 0,
                zoom: 4,
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
            const x = this.state.view.x + (this.state.pan.dx - event.clientX);
            const y = this.state.view.y + (this.state.pan.dy - event.clientY);

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
        const direction = event.deltaY / 100;
        const maxZoom = this.props.zoom?.max ?? 10;
        const minZoom = this.props.zoom?.min ?? 1;

        let { zoom } = this.state.view;
        zoom -= direction;
        zoom = Math.min(zoom, maxZoom);
        zoom = Math.max(zoom, minZoom);

        this.setState({
            view: { ...this.state.view, zoom },
        });

        this.redraw();
    };

    protected renderAxisLines() {
        // TODO: Fix incorrect line drawing on odd aspect ratios.
        //  Need to somehow read the width of the element and convert it to SVG units.
        let { x, y } = this.state.view;
        let bounds = this.viewboxRef.current?.viewBox.animVal;

        if (!bounds) {
            return [];
        }

        // desired increments for the lines
        const lrd = this.props.axisLines?.x; // left to right delta
        const tbd = this.props.axisLines?.y; // top to bottom delta

        let key: number = 0;
        const elements: JSX.Element[] = [];

        if (lrd) {
            let rx = Math.floor(y / lrd) * lrd;
            for (let dx = rx; dx < y + bounds.height; dx += lrd) {
                elements.push(
                    <line
                        key={`axline-${key++}`}
                        x1={x}
                        y1={dx}
                        x2={x + bounds.width}
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
            for (let dy = ry; dy < x + bounds.width; dy += tbd) {
                elements.push(
                    <line
                        key={`axline-${key++}`}
                        x1={dy}
                        y1={y}
                        x2={dy}
                        y2={y + bounds.height}
                        stroke={'black'}
                        strokeWidth={0.25}
                        opacity={0.25}
                    />
                );
                elements.push(
                    <text
                        key={`axline-text-${key++}`}
                        x={dy}
                        y={y + bounds.height}
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
        this.redraw();
    }

    public redraw() {
        // TODO: Can we fix this so we don't need to render thrice to achieve accurate results?
        // data needed for axline rendering is only(?) available after multiple renders
        this.forceUpdate(() => this.forceUpdate());
    }

    render() {
        const { x, y, zoom } = this.state.view;
        const bounds = this.viewboxRef.current?.getBoundingClientRect();

        if (bounds === undefined) {
            return <svg ref={this.viewboxRef} width={'100%'} height={'400px'} />;
        }

        const w = bounds.width;
        const h = bounds.height;

        return (
            <svg
                width={'100%'}
                height={'400px'}
                viewBox={`${x} ${y} ${w / zoom} ${h / zoom}`}
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
