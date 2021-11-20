# version 330 core

in vec3 vertexColor;
in vec3 vertexNormal;

out vec4 fragmentColor;

void main() {

    highp vec3 ka = vec3(0.05);
    highp vec3 kd = vec3(0.8, 0.8, 0.8);
    highp vec3 ks = vec3(0.5, 0.5, 0.5);
    highp float alpha = 2.0;

    highp vec3 ia = vec3(1.0);
    highp vec3 id = vec3(1.0);
    highp vec3 is = vec3(1.0);

    highp vec3 L = normalize(vec3(1.0, 1.0, 1.0));
    highp vec3 N = normalize(vertexNormal);
    highp vec3 V = normalize(vec3(0.0, 0.0, 1.0));
    highp vec3 R = reflect(L, N);

    highp float df = max(0.0, dot(L, N));
    highp float sf = pow(max(0.0, dot(R, V)), alpha);

    highp vec3 Ip = ka * ia + kd * id * df + ks*is*sf;

	fragmentColor = vec4(Ip, 1.0);
}