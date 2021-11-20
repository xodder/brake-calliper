# version 330 core

layout(location=0) in vec3 position;
layout(location=1) in vec3 normal;

out vec3 vertexColor;
out vec3 vertexNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

void main() {
	gl_Position = proj * view * model * vec4(position, 1.0);
	vertexColor = vec3(1.0, 1.0, 1.0);
	vertexNormal = mat3(transpose(inverse(model * view))) * normal;
}