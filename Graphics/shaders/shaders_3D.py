VERTEX_SHADER_3D_TAMING_SCENE = """
#version 330 core
in vec3 in_pos;
uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
void main() {
    gl_Position = m_proj * m_view * m_model * vec4(in_pos, 1.0);
}
"""
 
FRAGMENT_SHADER_3D_TAMING_SCENE = """
#version 330 core
uniform vec3 u_color;
out vec4 fragColor;
void main() {
    fragColor = vec4(u_color, 1.0);
}
"""

VERTEX_SHADER_3D = """
#version 330 core
in vec3 in_pos;
in vec3 in_instance_pos;
in float in_instance_type;

uniform mat4 m_proj;
uniform mat4 m_view;

out vec3 v_world_pos;
out float v_type;

void main() {

    vec3 world = in_pos + in_instance_pos;
    v_world_pos = world;
    v_type = in_instance_type;
    gl_Position = m_proj * m_view * vec4(world, 1.0);

}

"""

 

FRAGMENT_SHADER_3D = """

#version 330 core
in vec3 v_world_pos;
in float v_type;

uniform vec3 u_wall_color;
uniform vec3 u_portal_color;
uniform vec3 u_player_pos;
uniform float u_max_dist;

out vec4 fragColor;

void main() {

    float dist = length(v_world_pos.xz - u_player_pos.xz);
    float dimer = max(0.0, 1.0 - dist / u_max_dist);
    dimer = pow(dimer, 1.5);

int t = int(v_type + 0.5);
vec3 base;
if (t == 1) base = u_wall_color;
else if (t == 3) base = u_portal_color;
else if (t == 4) base = vec3(1.0, 0.0, 0.0);
else base = vec3(0.5, 0.5, 0.5);

if (t == 1) {

float row = floor(v_world_pos.y * 3.0);
float offset = mod(row, 2.0) * 0.5;
float bx = fract((v_world_pos.x + v_world_pos.z + offset) * 2.0);
float by = fract(v_world_pos.y * 3.0);

float mx = 1.0 - step(0.07, bx);
float my = 1.0 - step(0.09, by);
float mortar = max(mx, my);

base = mix(base, base * 0.3, mortar);
}

fragColor = vec4(base * dimer, 1.0);
}
"""