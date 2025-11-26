#version 300 es
precision highp float;

const int numLights = 25;

in vec3 v_normal;
in vec3 v_surfaceToLight[numLights];
in vec3 v_surfaceToView;

// Scene uniforms
uniform vec4 u_ambientLight[numLights];
uniform vec4 u_diffuseLight[numLights];
uniform vec4 u_specularLight[numLights];

// Model uniforms
uniform vec4 u_ambientColor;
uniform vec4 u_diffuseColor;
uniform vec4 u_specularColor;
uniform float u_shininess;

out vec4 outColor;

void main() {
    vec3 normal = normalize(v_normal);
    vec3 surfToViewDirection = normalize(v_surfaceToView);

    vec4 ambientAccum  = vec4(0.0);
    vec4 diffuseAccum  = vec4(0.0);
    vec4 specularAccum = vec4(0.0);

    for (int i = 0; i < numLights; ++i) {
        vec3 surfToLightDirection = normalize(v_surfaceToLight[i]);

        // Reflection vector
        vec3 r = normalize(2.0 * dot(normal, surfToLightDirection) * normal - surfToLightDirection);

        // Phong components
        float diffuse  = max(dot(normal, surfToLightDirection), 0.0);
        float specular = pow(max(dot(r, surfToViewDirection), 0.0), u_shininess);

        ambientAccum  += u_ambientLight[i]  * u_ambientColor;
        diffuseAccum  += u_diffuseLight[i]  * u_diffuseColor  * diffuse;
        specularAccum += u_specularLight[i] * u_specularColor * specular;
    }

    outColor = ambientAccum + diffuseAccum + specularAccum;
}


