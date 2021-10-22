import React from 'react';
import { ViewRect } from '../util/ViewRect';
import { rgb } from 'd3';
import { Line } from '../types/Line';

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
            const panFactor = 5;
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
        let { x, y, w, h } = this.state.view;

        // desired increments for the lines
        const tx = this.props.axisLines?.x;
        const ty = this.props.axisLines?.y;

        const lines: Line[] = [];

        // note the lines are across the specified axis, so for x lines we look at y values
        if (tx) {
            let rx = Math.floor(y / tx) * tx;
            for (let dx = rx; dx < y + h; dx += tx) {
                lines.push({
                    x1: x,
                    y1: dx,
                    x2: x + w,
                    y2: dx,
                });
            }
        }

        if (ty) {
            let ry = Math.floor(x / ty) * ty;
            for (let dy = ry; dy < x + w; dy += ty) {
                lines.push({
                    x1: dy,
                    y1: y,
                    x2: dy,
                    y2: y + h,
                });
            }
        }

        return lines.map(({ x1, y1, x2, y2 }, index) => (
            <line key={index} x1={x1} y1={y1} x2={x2} y2={y2} stroke={'rgba(0,0,0,0.25)'} strokeWidth={0.25} />
        ));
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
