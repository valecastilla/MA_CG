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
  grounds,
  initAgentsModel,
  update,
  getAgents,
  getObstacles,
  getTrafficLights,
  getDestinations,
  getRoads,
  getGrounds,
} from "../libs/api_connection.js";

import vsGLSL from "../assets/shaders/vs_phong_302.glsl?raw";
import fsGLSL from "../assets/shaders/fs_phong_302.glsl?raw";

//import vsGLSL from "../assets/shaders/vs_multi_lights_attenuation.glsl?raw";
//import fsGLSL from "../assets/shaders/fs_multi_lights_attenuation.glsl?raw";

// Destination
import objTextDestination from "../assets/obj/3d/canasta/canasta1.obj?raw";
import destinationMltText from "../assets/obj/3d/canasta/canasta.mtl?raw";

// Create vec to store obstacles objects to then chose them randomly
let obstacleObjects = [];
let obstacleMtlObjects = [];
import objTextObstacle1 from "../assets/obj/3d/arbol1.obj?raw";
import obstacle1MltText from "../assets/obj/3d/arbol1.mtl?raw";
obstacleObjects.push(objTextObstacle1);
obstacleMtlObjects.push(obstacle1MltText);
import objTextObstacle2 from "../assets/obj/3d/arboles/arbol2.obj?raw";
import obstacle2MltText from "../assets/obj/3d/arboles/arbol2.mtl?raw";
obstacleObjects.push(objTextObstacle2);
obstacleMtlObjects.push(obstacle2MltText);
import objTextObstacle3 from "../assets/obj/3d/arboles/arbol3.obj?raw";
import obstacle3MltText from "../assets/obj/3d/arboles/arbol3.mtl?raw";
obstacleObjects.push(objTextObstacle3);
obstacleMtlObjects.push(obstacle3MltText);
import objTextObstacle4 from "../assets/obj/3d/arboles/arbol4.obj?raw";
import obstacle4MltText from "../assets/obj/3d/arboles/arbol4.mtl?raw";
obstacleObjects.push(objTextObstacle4);
obstacleMtlObjects.push(obstacle4MltText);
import objTextObstacle5 from "../assets/obj/3d/arboles/arbol5.obj?raw";
import obstacle5MltText from "../assets/obj/3d/arboles/arbol5.mtl?raw";
obstacleObjects.push(objTextObstacle5);
obstacleMtlObjects.push(obstacle5MltText);
import objTextObstacle6 from "../assets/obj/3d/arboles/arbol6.obj?raw";
import obstacle6MltText from "../assets/obj/3d/arboles/arbol6.mtl?raw";
obstacleObjects.push(objTextObstacle6);
obstacleMtlObjects.push(obstacle6MltText);
import objTextObstacle7 from "../assets/obj/3d/arboles/arbol7.obj?raw";
import obstacle7MltText from "../assets/obj/3d/arboles/arbol7.mtl?raw";
obstacleObjects.push(objTextObstacle7);
obstacleMtlObjects.push(obstacle7MltText);
import objTextObstacle8 from "../assets/obj/3d/arboles/arbol8.obj?raw";
import obstacle8MltText from "../assets/obj/3d/arboles/arbol8.mtl?raw";
obstacleObjects.push(objTextObstacle8);
obstacleMtlObjects.push(obstacle8MltText);
import objTextObstacle9 from "../assets/obj/3d/arboles/arbol9.obj?raw";
import obstacle9MltText from "../assets/obj/3d/arboles/arbol9.mtl?raw";
obstacleObjects.push(objTextObstacle9);
obstacleMtlObjects.push(obstacle9MltText);

// Traffic Agents
import objTextTraffic from "../assets/obj/3d/trafficlight/semaforo.obj?raw";
//import obstacle8MltText from '../assets/obj/3d/edificios/tronco.mtl?raw';

// Agents
let agentObjects = [];
import objTextAgent1 from "../assets/obj/3d/huevos/huevo1.obj?raw";
import agent1MltText from "../assets/obj/3d/edificios/tronco.mtl?raw";
agentObjects.push(objTextAgent1);

// Pasto
let groundObjects = [];
let groundMtlObjects = [];
import objTextGround from "../assets/obj/3d/pastos/grass1.obj?raw";
import groundMltText from "../assets/obj/3d/pastos/grass1.mtl?raw";
groundObjects.push(objTextGround);
groundMtlObjects.push(groundMltText);
import objTextGround2 from "../assets/obj/3d/pastos/grass2.obj?raw";
import ground2MltText from "../assets/obj/3d/pastos/grass2.mtl?raw";
groundObjects.push(objTextGround2);
groundMtlObjects.push(ground2MltText);
import objTextGround3 from "../assets/obj/3d/pastos/grass3.obj?raw";
import ground3MltText from "../assets/obj/3d/pastos/grass3.mtl?raw";
groundObjects.push(objTextGround3);
groundMtlObjects.push(ground3MltText);
import objTextGround4 from "../assets/obj/3d/pastos/grass4.obj?raw";
import ground4MltText from "../assets/obj/3d/pastos/grass4.mtl?raw";
groundObjects.push(objTextGround4);
groundMtlObjects.push(ground4MltText);

// Road
let roadObjects = [];
let roadMtlObjects = [];
import objTextRoad1 from "../assets/obj/3d/tierra/tierra1.obj?raw";
import road1MltText from "../assets/obj/3d/tierra/tierra1.mtl?raw";
roadObjects.push(objTextRoad1);
roadMtlObjects.push(road1MltText);
import objTextRoad2 from "../assets/obj/3d/tierra/tierra2.obj?raw";
import road2MltText from "../assets/obj/3d/tierra/tierra2.mtl?raw";
roadObjects.push(objTextRoad2);
roadMtlObjects.push(road2MltText);
import objTextRoad3 from "../assets/obj/3d/tierra/tierra3.obj?raw";
import road3MltText from "../assets/obj/3d/tierra/tierra3.mtl?raw";
roadObjects.push(objTextRoad3);
roadObjects.push(objTextRoad3);
roadMtlObjects.push(road3MltText);
roadMtlObjects.push(road3MltText);
import objTextRoad4 from "../assets/obj/3d/tierra/tierra4.obj?raw";
import road4MltText from "../assets/obj/3d/tierra/tierra4.mtl?raw";
roadObjects.push(objTextRoad4);
roadMtlObjects.push(road4MltText);

// Sky box
import objTextSkybox from "../assets/models/skybox.obj?raw";

const baseCube = new Object3D(-1);
const littleA = new Object3D(-50);

const scene = new Scene3D();

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
  await getGrounds();

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
    const diffuse = baseColor; // Color dependent on state
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

  // Skybox
  const skybox = new Object3D(-7);
  skybox.prepareVAO(gl, programInfo, objTextSkybox);
  skybox.translation = { x: 11.0, y: 0.0, z: 11.0 };
  skybox.scale = { x: 1.25, y: 2.0, z: 1.25 };
  skybox.color = [119/255, 150/255, 203/255, 1.0];
  scene.addObject(skybox);

  // Obstacles
  let obstacleObjects3d = [];
  for (let i = 0; i < obstacleObjects.length; i++) {
    loadMtl(obstacleMtlObjects[i]);
    const obstacle = new Object3D(-2);
    obstacle.prepareVAO(gl, programInfo, obstacleObjects[i]);
    obstacleObjects3d.push(obstacle);
  }

  // Traffic Light
  const trafficLObj = new Object3D(-3, [1, 5, 1]);
  trafficLObj.prepareVAO(gl, programInfo, objTextTraffic);

  // Destination
  //loadMtl(destinationMltText);
  const destinationObj = new Object3D(-4);
  destinationObj.prepareVAO(gl, programInfo, objTextDestination);

  // Roads
  let roadObjects3d = [];
  for (let i = 0; i < roadObjects.length; i++) {
    loadMtl(roadMtlObjects[i]);
    const roadObj = new Object3D(-5);
    roadObj.prepareVAO(gl, programInfo, roadObjects[i]);
    roadObjects3d.push(roadObj);
  }

  // Grounds
  let groundObjects3d = [];
  for (let i = 0; i < groundObjects.length; i++) {
    loadMtl(groundMtlObjects[i]);
    const groundObj = new Object3D(-6);
    groundObj.prepareVAO(gl, programInfo, groundObjects[i]);
    groundObjects3d.push(groundObj);
  }

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

    agent.scale = { x: 0.1, y: 0.1, z: 0.1 };
    agent.color = baseObstacleObject.color;
    if (index == 0) {
      agent.scale = { x: 0.03, y: 0.08, z: 0.05 };
      agent.translation = { x: 0.0, y: -0.5, z: 0.0 };
    } else if (index == 1) {
      agent.scale = { x: 0.3, y: 0.3, z: 0.3 };
    } else if (index == 2) {
      agent.scale = { x: 0.18, y: 0.2, z: 0.18 };
      agent.translation = { x: 0.0, y: -0.5, z: 0.0 };
    } else if (index == 3) {
      agent.scale = { x: 0.1, y: 0.13, z: 0.15 };
    } else if (index == 4) {
      agent.scale = { x: 0.3, y: 0.3, z: 0.3 };
    } else if (index == 5) {
      agent.scale = { x: 0.09, y: 0.12, z: 0.09 };
      agent.translation = { x: 0.0, y: -0.5, z: 0.0 };
    } else if (index == 6) {
      agent.scale = { x: 0.4, y: 0.45, z: 0.4 };
    } else if (index == 7) {
      agent.scale = { x: 0.3, y: 0.35, z: 0.3 };
    } else if (index == 8) {
      agent.scale = { x: 0.4, y: 0.4, z: 0.4 };
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
      ? [122 / 255, 155 / 255, 118 / 255, 1.0] // green
      : [1.0, 0.0, 0.0, 1.0]; // red
    agent.forceColor = true;
    scene.addObject(agent);
  }

  for (const agent of destinations) {
    agent.arrays = destinationObj.arrays;
    agent.bufferInfo = destinationObj.bufferInfo;
    agent.vao = destinationObj.vao;
    agent.translation = { x: 0.0, y: 0.2, z: 0.0 };
    // Paint basket random color
    agent.color = [Math.random(), Math.random(), Math.random(), 1.0];
    agent.forceColor = true;
    agent.scale = { x: 0.0075, y: 0.0075, z: 0.0075 };
    scene.addObject(agent);
  }

  for (const agent of roads) {
    const index = Math.floor(randRange(0, roadObjects3d.length));
    const roadObj = roadObjects3d[index];

    agent.arrays = roadObj.arrays;
    agent.bufferInfo = roadObj.bufferInfo;
    agent.vao = roadObj.vao;
    agent.translation = { x: 0.0, y: -0.4, z: 0.0 };
    agent.scale = { x: 0.055, y: 0.01, z: 0.055 };
    agent.color = roadObj.color;
    scene.addObject(agent);
  }

  for (const agent of grounds) {
    const index = Math.floor(randRange(0, groundObjects3d.length));
    const groundObj = groundObjects3d[index];
    agent.arrays = groundObj.arrays;
    agent.bufferInfo = groundObj.bufferInfo;
    agent.vao = groundObj.vao;
    agent.translation = { x: 0.0, y: -0.3, z: 0.0 };
    agent.scale = { x: 0.06, y: 0.01, z: 0.06 };
    agent.color = groundObj.color;
    scene.addObject(agent);
  }
}

// Draw an object with its corresponding transformations
function drawObject(gl, programInfo, object, viewProjectionMatrix, fract) {
  // Prepare the vector for translation and scale
  let v3_tra = object.posArray;
  let v3_sca = object.scaArray;

  if (object.oldPosArray && object.posArray) {
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
    // Texture and color depending on object properties
    u_useDiffuseMap: object.texture ? true : false,
    u_forceDiffuseColor: object.forceColor ? true : false,
    u_diffuseMap: object.texture,
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

  for (let i = 0; i < agents.length; i++) {
    const agent = agents[i];
    // If the agent id already exists, skip
    const existingAgent = scene.objects.find((o) => o.id === agent.id);
    if (existingAgent) continue;

    agent.arrays = baseCube.arrays;
    agent.bufferInfo = baseCube.bufferInfo;
    agent.vao = baseCube.vao;
    agent.scale = { x: 0.25, y: 0.35, z: 0.25 };
    agent.translation = { x: 0.0, y: 0.1, z: 0.0 };
    agent.forceColor = true;
    agent.color = [Math.random(), Math.random(), Math.random(), 1.0]; // Random colorw

    // Create a unique little sub-object for this agent
    const littleA = new Object3D(-2000 - i);
    littleA.arrays = agent.arrays;
    littleA.bufferInfo = agent.bufferInfo;
    littleA.vao = agent.vao;
    littleA.scale = { x: 0.1, y: 0.15, z: 0.1 };
    littleA.translation = { x: 0.0, y: 0.1, z: 0.0 }; // Inside the same cell
    littleA.forceColor = true;
    littleA.color = [Math.random(), Math.random(), Math.random(), 1.0]; // Random color

    // Attach to the main agent
    agent.subObject = littleA;

    // Rotating little egg parameters
    littleA.rotatingRadius = 0.4;
    littleA.rotatingAngle = Math.random() * Math.PI * 2; // Random start angle

    scene.addObject(agent);
    scene.addObject(littleA);
  }

  // Make the little agents orbit around their parent agents using `fract`
  for (const agent of agents) {
    const sub = agent.subObject;
    if (!sub) continue;

    const center = agent.posArray; // Center is bigger egg position
    const radius = sub.rotatingRadius;
    const baseAngle = sub.rotatingAngle;

    // One full turn per "duration" (1 second): angle = base + fract * 2π
    const angle = baseAngle + (fract*2.5) * 2 * Math.PI;

    // Calculate next pos in radius using polar coordinates
    const rotationX = Math.cos(angle) * radius;
    const rotationZ = Math.sin(angle) * radius;

    sub.position.x = center[0] + rotationX;
    sub.position.y = center[1]; // Same current y
    sub.position.z = center[2] + rotationZ;
  }

  // Update traffic light objects colors
  for (const tl of trafficLights) {
    const baseColor = tl.state
      ? [0.45, 0.9, 0.27, 1.0]
      : [255 / 255, 66 / 255, 63 / 255, 1.0];

    // Update light linked to this traffic light
    const light = scene.lights.find((l) => l.trafficId === tl.id);
    if (light) {
      light.ambient = [0.2, 0.2, 0.2, 1.0];
      light.diffuse = baseColor;
    }

    // Update the object color
    const obj = scene.objects.find(
      (o) => o.id === tl.id || o.trafficId === tl.id
    );
    if (obj) {
      obj.color = baseColor;
    }
  }

  for (let object of scene.objects) {
    drawObject(gl, phongProgramInfo, object, viewProjectionMatrix, fract);
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

  const globalUniforms = {
    u_viewWorldPosition: scene.camera.posArray,
    u_lightWorldPosition: lightPositions,
    u_ambientLight: ambientLights,
    u_diffuseLight: diffuseLights,
    u_specularLight: specularLights,
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
