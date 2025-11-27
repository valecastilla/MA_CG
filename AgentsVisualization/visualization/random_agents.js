/*
 * Base program for a 3D scene that connects to an API to get the movement
 * of agents.
 * The scene shows colored cubes
 *
 * Gilberto Echeverria
 * 2025-11-08
 */

"use strict";

import * as twgl from "twgl-base.js";
import GUI from "lil-gui";
import { M4 } from "../libs/3d-lib";
import { Scene3D } from "../libs/scene3d";
import { generateConeOBJ } from "../libs/cg2.js";
import { Object3D } from "../libs/object3d";
import { Light3D } from "../libs/light3d";
import { Camera3D } from "../libs/camera3d";

import { loadMtl } from "../libs/obj_loader.js";
//import

// Functions and arrays for the communication with the API
import {
  agents,
  obstacles,
  trafficLights,
  destinations,
  roads,
  initAgentsModel,
  update,
  getAgents,
  getObstacles,
  getTrafficLights,
  getDestinations,
  getRoads,
} from "../libs/api_connection.js";

import vsGLSL from "../assets/shaders/vs_phong_302.glsl?raw";
import fsGLSL from "../assets/shaders/fs_phong_302.glsl?raw";

//import vsGLSL from "../assets/shaders/vs_multi_lights_attenuation.glsl?raw";
//import fsGLSL from "../assets/shaders/fs_multi_lights_attenuation.glsl?raw";

// Chatgpt function to convert file into string
function loadText(path) {
  const xhr = new XMLHttpRequest();
  xhr.open("GET", path, false); // false = synchronous
  xhr.send(null);
  return xhr.status >= 200 && xhr.status < 300 ? xhr.responseText : "";
}

const objTextDestination = loadText("../assets/obj/3d/canasta/canasta1.obj");
import destinationMltText from "../assets/obj/3d/canasta/canasta.mtl?raw";

// Create vec to store obstacles objects to then chose them randomly
let obstacleObjects = [];
const objTextObstacle1 = loadText("../assets/obj/3d/edificios/arbol1.obj");
import obstacle1MltText from "../assets/obj/3d/edificios/arbol1.mtl?raw";
obstacleObjects.push(objTextObstacle1);

const objTextObstacle2 = loadText("../assets/obj/3d/edificios/arbol2.obj");
import obstacle2MltText from "../assets/obj/3d/edificios/arbol2.mtl?raw";
obstacleObjects.push(objTextObstacle2);

const objTextObstacle3 = loadText("../assets/obj/3d/edificios/arbol3.obj");
import obstacle3MltText from "../assets/obj/3d/edificios/arbol3.mtl?raw";
obstacleObjects.push(objTextObstacle3);

// const objTextObstacle4 = loadText("../assets/obj/3d/edificios/maleza.obj");
// import obstacle4MltText from '../assets/obj/3d/edificios/maleza.mtl?raw';
// obstacleObjects.push(objTextObstacle4);

const objTextObstacle5 = loadText("../assets/obj/3d/edificios/roca1.obj");
import obstacle5MltText from "../assets/obj/3d/edificios/roca1.mtl?raw";
obstacleObjects.push(objTextObstacle5);

// const objTextObstacle6 = loadText("../assets/obj/3d/edificios/roca2.obj");
// import obstacle6MltText from '../assets/obj/3d/edificios/roca2.mtl?raw';
// obstacleObjects.push(objTextObstacle6);

const objTextObstacle7 = loadText("../assets/obj/3d/edificios/roca3.obj");
import obstacle7MltText from "../assets/obj/3d/edificios/roca3.mtl?raw";
obstacleObjects.push(objTextObstacle7);

const objTextObstacle8 = loadText("../assets/obj/3d/edificios/tronco.obj");
import obstacle8MltText from "../assets/obj/3d/edificios/tronco.mtl?raw";
obstacleObjects.push(objTextObstacle8);

// Traffic Agents
const objTextTraffic = loadText("../assets/obj/3d/trafficlight/semaforo.obj");
//import obstacle8MltText from '../assets/obj/3d/edificios/tronco.mtl?raw';

// Agents
let agentObjects = [];
const objTextAgent1 = loadText("../assets/obj/3d/huevos/huevo1.obj");
import agent1MltText from "../assets/obj/3d/edificios/tronco.mtl?raw";
agentObjects.push(objTextAgent1);

// Pasto
const objTextRoad = loadText("../assets/obj/3d/roads/grass.obj");
import roadMltText from "../assets/obj/3d/grass.mtl?raw";
const objTextRoad2 = loadText("../assets/obj/3d/roads/grass2.obj");
import road2MltText from "../assets/obj/3d/roads/grass2.mtl?raw";
// Road


const baseCube = new Object3D(-1);

const scene = new Scene3D();

/*
// Variable for the scene settings
const settings = {
    // Speed in degrees
    rotationSpeed: {
        x: 0,
        y: 0,
        z: 0,
    },
};
*/

// Global variables
let phongProgramInfo = undefined;
let gl = undefined;
const duration = 1000; // ms
let elapsed = 0;
let then = 0;

// Main function is async to be able to make the requests
async function main() {
  // Setup the canvas area
  const canvas = document.querySelector("canvas");
  gl = canvas.getContext("webgl2");
  twgl.resizeCanvasToDisplaySize(gl.canvas);
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

  // Prepare the program with the shaders
  phongProgramInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

  // Initialize the agents model
  await initAgentsModel();

  // Get the agents, obstacles, traffic lights, destinations and roads
  await getAgents();
  await getObstacles();
  await getTrafficLights();
  await getDestinations();
  await getRoads();

  // Initialize the scene
  setupScene();

  // Position the objects in the scene
  setupObjects(scene, gl, phongProgramInfo);

  // Prepare the user interface
  setupUI();

  // Fisrt call to the drawing loop
  drawScene();
}

function setupScene() {
  let camera = new Camera3D(
    0,
    10, // Distance to target
    4, // Azimut
    0.8, // Elevation
    [0, 0, 10],
    [0, 0, 0]
  );
  // These values are empyrical.
  // Maybe find a better way to determine them
  camera.panOffset = [0, 8, 0];
  scene.setCamera(camera);
  scene.camera.setupControls();

  let light = new Light3D(
    0,
    [3, 3, 5], // Position
    [0.3, 0.3, 0.3, 1.0], // Ambient
    [1.0, 1.0, 1.0, 1.0], // Diffuse
    [1.0, 1.0, 1.0, 1.0]
  ); // Specular

  scene.addLight(light);

  // Traffic lights as lights
  const numLights = 25;
  let nextLightIndex = 1; // 0 is the sun

  for (const tl of trafficLights) {
    if (nextLightIndex >= numLights) {
      break;
    }

    // Get color for light from current state
    const baseColor = tl.state
      ? [0.0, 1.0, 0.0, 1.0] // green
      : [1.0, 0.0, 0.0, 1.0]; // red

    const ambient = [0.0, 0.0, 0.0, 1.0];
    const diffuse = baseColor; // color dependent on state
    const specular = [1.0, 1.0, 1.0, 1.0];

    const pos = [tl.position.x, tl.position.y, tl.position.z];

    const light = new Light3D(nextLightIndex, pos, ambient, diffuse, specular);

    // Save which traffic light this light belongs to
    light.trafficId = tl.id;

    scene.addLight(light);
    nextLightIndex++;
  }
}

function randRange(min, max) {
  return min + Math.random() * (max - min);
}

function setupObjects(scene, gl, programInfo) {
  // Create VAOs for the different shapes
  //baseCube = new Object3D(-1);
  baseCube.prepareVAO(gl, programInfo, objTextAgent1);
  // Use objloader function with

  // Array to save the obstacle objects
  let obstacleObjects3d = [];
  loadMtl(obstacle1MltText);
  const obstacle1 = new Object3D(-2);
  obstacle1.prepareVAO(gl, programInfo, obstacleObjects[0]);
  console.log("arbol1 base color:", obstacle1.color);
  obstacleObjects3d.push(obstacle1);
  loadMtl(obstacle2MltText);
  const obstacle2 = new Object3D(-2);
  obstacle2.prepareVAO(gl, programInfo, obstacleObjects[1]);
  obstacleObjects3d.push(obstacle2);
  //loadMtl(obstacle3MltText);
  const obstacle3 = new Object3D(-2);
  obstacle3.prepareVAO(gl, programInfo, obstacleObjects[2]);
  obstacleObjects3d.push(obstacle3);
  //loadMtl(obstacle5MltText);
  const obstacle4 = new Object3D(-2);
  obstacle4.prepareVAO(gl, programInfo, obstacleObjects[3]);
  obstacleObjects3d.push(obstacle4);
  //loadMtl(obstacle7MltText);
  const obstacle5 = new Object3D(-2);
  obstacle5.prepareVAO(gl, programInfo, obstacleObjects[4]);
  obstacleObjects3d.push(obstacle5);
  //loadMtl(obstacle8MltText);
  const obstacle6 = new Object3D(-2);
  obstacle6.prepareVAO(gl, programInfo, obstacleObjects[5]);
  obstacleObjects3d.push(obstacle6);
  //loadMtl(destinationMltText);

  // Traffic Light
  const trafficLObj = new Object3D(-3, [1, 5, 1]);
  trafficLObj.prepareVAO(gl, programInfo, objTextTraffic);

  // Destination
  //loadMtl(destinationMltText);
  const destinationObj = new Object3D(-4);
  destinationObj.prepareVAO(gl, programInfo, objTextDestination);

  // Roads
  loadMtl(road2MltText);
  const roadObj = new Object3D(-5);
  roadObj.prepareVAO(gl, programInfo, objTextRoad2);
  

  /*
  // A scaled cube to use as the ground
  const ground = new Object3D(-3, [14, 0, 14]);
  ground.arrays = baseCube.arrays;
  ground.bufferInfo = baseCube.bufferInfo;
  ground.vao = baseCube.vao;
  ground.scale = {x: 50, y: 0.1, z: 50};
  ground.color = [0.6, 0.6, 0.6, 1];
  scene.addObject(ground);
  */

  // Copy the properties of the base objects
  for (const agent of agents) {
    agent.arrays = baseCube.arrays;
    agent.bufferInfo = baseCube.bufferInfo;
    agent.vao = baseCube.vao;
    agent.scale = { x: 1.0, y: 1.0, z: 1.0 };
    scene.addObject(agent);
  }

  // Copy the properties of the base objects
  for (const agent of obstacles) {
    const index = Math.floor(randRange(0, obstacleObjects.length));
    const baseObstacleObject = obstacleObjects3d[index];

    agent.arrays = baseObstacleObject.arrays;
    agent.bufferInfo = baseObstacleObject.bufferInfo;
    agent.vao = baseObstacleObject.vao;

    //agent.color = [0.0, 0.0, 1.0, 1.0];

    agent.scale = { x: 0.1, y: 0.1, z: 0.1 };
    if (index == 5) {
      agent.scale = { x: 1.0, y: 1.0, z: 1.0 };
      // Make tronco colored brown
      agent.color = [0.55, 0.27, 0.07, 1.0];
      //agent.translation = { x: 0, y: 3, z: 0 };
    }
    // Arbol
    else if (index == 0) {
      agent.scale = { x: 0.35, y: 0.35, z: 0.35 };
      agent.color = [34 / 255, 139 / 255, 50 / 255, 1.0];
    } else if (index == 1) {
      agent.scale = { x: 0.5, y: 0.4, z: 0.5 };
      agent.color = [34 / 255, 139 / 255, 34 / 255, 1.0];
    } else if (index == 2) {
      agent.scale = { x: 0.55, y: 0.5, z: 0.55 };
      agent.color = [98 / 255, 109 / 255, 88 / 255, 1.0];
    } else if (index == 3) {
      agent.scale = { x: 1.0, y: 1.0, z: 1.0 };
      agent.color = [116 / 255, 117 / 255, 120 / 255, 1.0];
    } else if (index == 4) {
      agent.scale = { x: 1.0, y: 1.0, z: 1.0 };
      agent.color = [116 / 255, 109 / 255, 117 / 255, 1.0];
    }
    scene.addObject(agent);
  }

  for (const agent of trafficLights) {
    agent.arrays = trafficLObj.arrays;
    agent.bufferInfo = trafficLObj.bufferInfo;
    agent.vao = trafficLObj.vao;
    agent.scale = { x: 2.0, y: 2.0, z: 2.0 };
    agent.translation = { x: 0.0, y: 1.5, z: 0.0 };
    agent.color = agent.state
      ? [0.0, 1.0, 0.0, 1.0] // green
      : [1.0, 0.0, 0.0, 1.0]; // red
    scene.addObject(agent);
  }

  for (const agent of destinations) {
    agent.arrays = destinationObj.arrays;
    agent.bufferInfo = destinationObj.bufferInfo;
    agent.vao = destinationObj.vao;
    agent.translation = { x: 0.0, y: 0.1, z: 0.0 };
    //agent.color = destinationObj.color;
    agent.scale = { x: 0.0075, y: 0.0075, z: 0.0075 };
    scene.addObject(agent);
  }

  for (const agent of roads) {
  //   const roadObj = new Object3D(-5, [14, 0, 14]);
  //   roadObj.prepareVAO(gl, programInfo);

  //   agent.arrays = roadObj.arrays;
  //   agent.bufferInfo = roadObj.bufferInfo;
  //   agent.vao = roadObj.vao;
  //   agent.scale = { x: 50, y: 0.1, z: 50 };
  //   agent.color = [49 / 255, 233 / 255, 150 / 255, 1.0];
  //   scene.addObject(agent);
  // }
    agent.arrays = roadObj.arrays;
    agent.bufferInfo = roadObj.bufferInfo;
    agent.vao = roadObj.vao;
    agent.translation = { x: 0.0, y: -0.4, z: 0.0 };
    agent.scale = { x: 0.075, y: 0.01, z: 0.075 };
    agent.color = roadObj.color;
    scene.addObject(agent);
}
}

// Draw an object with its corresponding transformations
function drawObject(gl, programInfo, object, viewProjectionMatrix, fract) {
  // Prepare the vector for translation and scale
  let v3_tra = object.posArray;
  let v3_sca = object.scaArray;

  if (
    object.oldPosArray &&
    object.posArray
  ) {
    const a = object.oldPosArray; // old position
    const b = object.posArray; // new position

    v3_tra = [
      a[0] + (b[0] - a[0]) * fract,
      object.oldPosArray[1],
      a[2] + (b[2] - a[2]) * fract,
    ];
  } else {
    // Static objects
    v3_tra = object.posArray;
  }

  if (object.translation) {
    v3_tra = [
      v3_tra[0] + object.translation.x,
      v3_tra[1] + object.translation.y,
      v3_tra[2] + object.translation.z,
    ];
  }

  /* // Animate the rotation of the objects
  object.rotDeg.x = (object.rotDeg.x + settings.rotationSpeed.x * fract) % 360;
  object.rotDeg.y = (object.rotDeg.y + settings.rotationSpeed.y * fract) % 360;
  object.rotDeg.z = (object.rotDeg.z + settings.rotationSpeed.z * fract) % 360;
  object.rotRad.x = object.rotDeg.x * Math.PI / 180;
  object.rotRad.y = object.rotDeg.y * Math.PI / 180;
  object.rotRad.z = object.rotDeg.z * Math.PI / 180; */

  // Create the individual transform matrices
  const scaMat = M4.scale(v3_sca);
  const rotXMat = M4.rotationX(object.rotRad.x);
  const rotYMat = M4.rotationY(object.rotRad.y);
  const rotZMat = M4.rotationZ(object.rotRad.z);
  const traMat = M4.translation(v3_tra);

  // Create the composite matrix with all transformations
  let transforms = M4.identity();
  transforms = M4.multiply(scaMat, transforms);
  transforms = M4.multiply(rotXMat, transforms);
  transforms = M4.multiply(rotYMat, transforms);
  transforms = M4.multiply(rotZMat, transforms);
  transforms = M4.multiply(traMat, transforms);

  object.matrix = transforms;

  // Apply the projection to the final matrix for the
  // World-View-Projection
  const wvpMat = M4.multiply(viewProjectionMatrix, transforms);

  const normalMat = M4.transpose(M4.inverse(object.matrix));

  // Model uniforms
  let objectUniforms = {
    u_world: object.matrix,
    u_worldInverseTransform: normalMat,
    u_worldViewProjection: wvpMat,

    u_ambientColor: object.color,
    u_diffuseColor: object.color,
    u_specularColor: object.color,
    u_shininess: object.shininess,
  };
  twgl.setUniforms(programInfo, objectUniforms);

  gl.bindVertexArray(object.vao);
  twgl.drawBufferInfo(gl, object.bufferInfo);
}

// Function to do the actual display of the objects
async function drawScene() {
  // Compute time elapsed since last frame
  let now = Date.now();
  let deltaTime = now - then;
  elapsed += deltaTime;
  let fract = Math.min(1.0, elapsed / duration);
  then = now;

  // Clear the canvas
  gl.clearColor(0, 0, 0, 1);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  // tell webgl to cull faces
  gl.enable(gl.CULL_FACE);
  gl.enable(gl.DEPTH_TEST);

  scene.camera.checkKeys();
  //console.log(scene.camera);
  const viewProjectionMatrix = setupViewProjection(gl);

  // Draw the objects
  gl.useProgram(phongProgramInfo.program);

  for (const agent of agents) {
    agent.arrays = baseCube.arrays;
    agent.bufferInfo = baseCube.bufferInfo;
    agent.vao = baseCube.vao;
    agent.scale = { x: 0.25, y: 0.35, z: 0.25 };
    scene.addObject(agent);
  }

  for (let object of scene.objects) {
    drawObject(gl, phongProgramInfo, object, viewProjectionMatrix, fract);
  }

  for (const tl of trafficLights) {
    const light = scene.lights.find((l) => l.trafficId === tl.id);
    if (!light) continue;

    const baseColor = tl.state
      ? [0.0, 1.0, 0.0, 1.0] // green
      : [1.0, 0.0, 0.0, 1.0]; // red

    light.ambient = [0.2, 0.2, 0.2, 1.0];

    light.diffuse = baseColor;
    // specular stay white
  }

  const numLights = 25;
  const lightPositions = [];
  const ambientLights = [];
  const diffuseLights = [];
  const specularLights = [];

  for (let i = 0; i < numLights; i++) {
    const light = scene.lights[i];

    if (light) {
      lightPositions.push(
        light.posArray[0],
        light.posArray[1],
        light.posArray[2]
      );

      ambientLights.push(
        light.ambient[0],
        light.ambient[1],
        light.ambient[2],
        light.ambient[3]
      );

      diffuseLights.push(
        light.diffuse[0],
        light.diffuse[1],
        light.diffuse[2],
        light.diffuse[3]
      );

      specularLights.push(
        light.specular[0],
        light.specular[1],
        light.specular[2],
        light.specular[3]
      );
    } else {
      // If no more lights
      lightPositions.push(0.0, 10000.0, 0.0);
      ambientLights.push(0.0, 0.0, 0.0, 1.0);
      diffuseLights.push(0.0, 0.0, 0.0, 1.0);
      specularLights.push(0.0, 0.0, 0.0, 1.0);
    }
  }

  const ambientLight = [0.2, 0.2, 0.2, 1.0];

  const globalUniforms = {
    u_viewWorldPosition: scene.camera.posArray,
    u_lightWorldPosition: lightPositions,
    u_ambientLight: ambientLight,
    u_diffuseLight: diffuseLights,
    u_specularLight: specularLights,
    u_constant: 1.0,
    u_linear: 0.09,
    u_quadratic: 0.032,
  };

  twgl.setUniforms(phongProgramInfo, globalUniforms);

  // Update the scene after the elapsed duration
  if (elapsed >= duration) {
    elapsed = 0;
    await update();
  }

  requestAnimationFrame(drawScene);
}

function setupViewProjection(gl) {
  // Field of view of 60 degrees vertically, in radians
  const fov = (60 * Math.PI) / 180;
  const aspect = gl.canvas.clientWidth / gl.canvas.clientHeight;

  // Matrices for the world view
  const projectionMatrix = M4.perspective(fov, aspect, 1, 200);

  const cameraPosition = scene.camera.posArray;
  const target = scene.camera.targetArray;
  const up = [0, 1, 0];

  const cameraMatrix = M4.lookAt(cameraPosition, target, up);
  const viewMatrix = M4.inverse(cameraMatrix);
  const viewProjectionMatrix = M4.multiply(projectionMatrix, viewMatrix);

  return viewProjectionMatrix;
}

// Setup a ui.
function setupUI() {
  /*
  const gui = new GUI();

  // Settings for the animation
  const animFolder = gui.addFolder('Animation:');
  animFolder.add( settings.rotationSpeed, 'x', 0, 360)
      .decimals(2)
  animFolder.add( settings.rotationSpeed, 'y', 0, 360)
      .decimals(2)
  animFolder.add( settings.rotationSpeed, 'z', 0, 360)
      .decimals(2)
  */
}


main();
