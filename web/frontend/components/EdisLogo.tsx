import React from 'react';

interface LogoProps {
  size?: number;
  className?: string;
}

export default function EdisLogo({ size = 48, className = '' }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="edis-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#667eea" />
          <stop offset="50%" stopColor="#764ba2" />
          <stop offset="100%" stopColor="#f093fb" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Abstract Neural Network Design */}
      {/* Central Core */}
      <circle
        cx="50"
        cy="50"
        r="12"
        fill="url(#edis-gradient)"
        filter="url(#glow)"
      />
      
      {/* Outer Nodes */}
      <circle cx="50" cy="20" r="6" fill="url(#edis-gradient)" opacity="0.8" />
      <circle cx="80" cy="35" r="6" fill="url(#edis-gradient)" opacity="0.8" />
      <circle cx="80" cy="65" r="6" fill="url(#edis-gradient)" opacity="0.8" />
      <circle cx="50" cy="80" r="6" fill="url(#edis-gradient)" opacity="0.8" />
      <circle cx="20" cy="65" r="6" fill="url(#edis-gradient)" opacity="0.8" />
      <circle cx="20" cy="35" r="6" fill="url(#edis-gradient)" opacity="0.8" />
      
      {/* Connecting Lines */}
      <line x1="50" y1="38" x2="50" y2="20" stroke="url(#edis-gradient)" strokeWidth="2" opacity="0.6" />
      <line x1="62" y1="44" x2="74" y2="35" stroke="url(#edis-gradient)" strokeWidth="2" opacity="0.6" />
      <line x1="62" y1="56" x2="74" y2="65" stroke="url(#edis-gradient)" strokeWidth="2" opacity="0.6" />
      <line x1="50" y1="62" x2="50" y2="80" stroke="url(#edis-gradient)" strokeWidth="2" opacity="0.6" />
      <line x1="38" y1="56" x2="26" y2="65" stroke="url(#edis-gradient)" strokeWidth="2" opacity="0.6" />
      <line x1="38" y1="44" x2="26" y2="35" stroke="url(#edis-gradient)" strokeWidth="2" opacity="0.6" />
      
      {/* Orbital Ring */}
      <circle
        cx="50"
        cy="50"
        r="35"
        stroke="url(#edis-gradient)"
        strokeWidth="1.5"
        fill="none"
        opacity="0.3"
        strokeDasharray="5,5"
      >
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 50 50"
          to="360 50 50"
          dur="20s"
          repeatCount="indefinite"
        />
      </circle>
    </svg>
  );
}
