import React from 'react';

interface ComponentProps {
    x: number;
    y: number;
    radius: number;
    stroke?: string;
    fill?: string;
}

export class Circle extends React.Component<ComponentProps, never> {
    render() {
        return (
            <svg>
                <circle
                    cx={this.props.x}
                    cy={this.props.y}
                    r={this.props.radius}
                    stroke={this.props.stroke}
                    fill={this.props.fill}
                />
            </svg>
        );
    }
}
