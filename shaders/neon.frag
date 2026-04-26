#version 330 core

out vec4 FragColor;

uniform vec3 neonColor;
uniform float intensity; // To modulate glow

void main()
{
    // A simple output. For real bloom we would typically use post-processing.
    // Here we can just output the color. The particle/line thickness and additive blending will create a fake neon glow.
    FragColor = vec4(neonColor * intensity, 1.0);
}
