#version 330 core

out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D textTexture;
uniform vec3 textColor;

void main()
{
    vec4 texColor = texture(textTexture, TexCoord);
    FragColor = vec4(textColor, 1.0) * texColor;
}
