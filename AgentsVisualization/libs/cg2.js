// cone_generator.js (ES module)

export function generateConeOBJ(side, height, baseRadius, topRadius) {
    let vertices = [];
    let faces = [];

    // Centers
    vertices.push([0, 0, 0]);          // base center
    vertices.push([0, height, 0]);     // top center

    // Ring vertices
    let angleStep = (2 * Math.PI) / side;
    for (let s = 0; s < side; s++) {
        let angle = angleStep * s;
        let xBase = baseRadius * Math.cos(angle);
        let zBase = baseRadius * Math.sin(angle);
        let xTop  = topRadius * Math.cos(angle);
        let zTop  = topRadius * Math.sin(angle);
        vertices.push([xBase, 0, zBase]);
        vertices.push([xTop, height, zTop]);
    }

    // Faces
    for (let s = 0; s < side; s++) {
        let n1 = s * 2 + 2;
        let n2 = ((s + 1) % side) * 2 + 2;
        let n3 = s * 2 + 3;
        let n4 = ((s + 1) % side) * 2 + 3;

        faces.push([n2, 0, n1]);  // base
        faces.push([n3, 1, n4]);  // top

        if (s === side - 1) {
            faces.push([n1, n3, n2]);  // side 1 last segment
        } else {
            faces.push([n2, n1, n3]);  // side 1
        }
        faces.push([n4, n2, n3]);      // side 2
    }

    // Build OBJ text
    let objInfo = [];

    // Vertices
    for (let i = 0; i < vertices.length; i++) {
        objInfo.push(`v ${vertices[i][0]} ${vertices[i][1]} ${vertices[i][2]}`);
    }

    // Helpers
    function sub(a, b) {
        return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    }
    function cross(a, b) {
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ];
    }
    function len(a) {
        return Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
    }
    function normalize(a) {
        let L = len(a) || 1;
        return [a[0] / L, a[1] / L, a[2] / L];
    }

    // One normal per face
    let normals = [];
    for (let i = 0; i < faces.length; i++) {
        let f = faces[i];
        let p1 = vertices[f[0]];
        let p2 = vertices[f[1]];
        let p3 = vertices[f[2]];

        if (f.includes(0)) {
            normals.push([0, -1, 0]);   // base
            continue;
        }
        if (f.includes(1)) {
            normals.push([0, 1, 0]);    // top
            continue;
        }

        let v1 = sub(p2, p1);
        let v2 = sub(p3, p1);
        let n  = normalize(cross(v1, v2));
        normals.push(n);
    }

    // Normals
    for (let i = 0; i < normals.length; i++) {
        objInfo.push(`vn ${normals[i][0]} ${normals[i][1]} ${normals[i][2]}`);
    }

    // Faces (vertex and normal indices)
    for (let i = 0; i < faces.length; i++) {
        let f = faces[i];
        let ni = i + 1;
        let v1 = f[0] + 1;
        let v2 = f[1] + 1;
        let v3 = f[2] + 1;
        objInfo.push(`f ${v1}//${ni} ${v2}//${ni} ${v3}//${ni}`);
    }

    return objInfo.join("\n");
}
