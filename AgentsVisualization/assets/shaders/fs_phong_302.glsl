#version 300 es
precision highp float;

const int numLights = 25;

in vec3 v_normal;
in vec3 v_surfaceToLight[numLights];
in vec3 v_surfaceToView;
in float v_lightDist2[numLights];
in vec4 v_color;
in vec2 v_texcoord;

// Scene uniforms
uniform vec4 u_ambientLight[numLights];
uniform vec4 u_diffuseLight[numLights];
uniform vec4 u_specularLight[numLights];

// Model uniforms
uniform vec4 u_ambientColor;
uniform vec4 u_diffuseColor;
uniform vec4 u_specularColor;
uniform float u_shininess;
uniform sampler2D u_diffuseMap;
uniform bool u_useDiffuseMap;
uniform bool u_forceDiffuseColor;

out vec4 outColor;

void main() {
    vec3 normal = normalize(v_normal);
    vec3 surfToViewDirection = normalize(v_surfaceToView);

    vec4 ambientAccum  = vec4(0.0);
    vec4 diffuseAccum  = vec4(0.0);
    vec4 specularAccum = vec4(0.0);

    for (int i = 0; i < numLights; ++i) {
        // Distancia ** 2 easier than distance
        float dist2 = v_lightDist2[i];

        // Max radius where light affects
        float maxRadius  = 2.0;           
        float maxRadius2 = maxRadius * maxRadius;

        // If its outside radius, dont affect
        if (dist2 > maxRadius2 && i > 0) {
            continue;
        }


        vec3 surfToLightDirection = normalize(v_surfaceToLight[i]);

        // Reflection vector
        vec3 r = normalize(2.0 * dot(normal, surfToLightDirection) * normal - surfToLightDirection);

        // Phong components
        float diffuse  = max(dot(normal, surfToLightDirection), 0.0);
        float specular = pow(max(dot(r, surfToViewDirection), 0.0), u_shininess);

        if (i > 0) {
            float attenuation = 1.0 - dist2 / maxRadius2; // Get a value between 0-1 depending on how close or far to radius
            attenuation = clamp(attenuation, 0.0, 1.0); // If value of attenuation is not between 0-1, change it
        }

        ambientAccum  += u_ambientLight[i];
        diffuseAccum  += u_diffuseLight[i] * diffuse;
        specularAccum += u_specularLight[i] * specular;
    }



    // Choose material color
    vec4 matColor;
    if (u_forceDiffuseColor) {
        matColor = u_diffuseColor;
    } else if (u_useDiffuseMap) {
        vec4 texc = texture(u_diffuseMap, v_texcoord);
        matColor = texc * u_diffuseColor;
    } else if (v_color.a > 0.0) { 
        matColor = v_color;
    } else {
        matColor = u_diffuseColor;
    }

    // Apply chosen material color once to ambient and diffuse
    vec4 finalAmbient  = ambientAccum * matColor;
    vec4 finalDiffuse  = diffuseAccum * matColor;
    vec4 finalSpecular = specularAccum * u_specularColor;

    outColor = finalAmbient + finalDiffuse + finalSpecular;
}