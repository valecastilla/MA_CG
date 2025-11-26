/*
 * Base program for a 3D scene that connects to an API to get the movement
 * of agents.
 * The scene shows colored cubes
 *
 * Gilberto Echeverria
 * 2025-11-08
 */


'use strict';

import * as twgl from 'twgl-base.js';
import GUI from 'lil-gui';
import { M4 } from '../libs/3d-lib';
import { Scene3D } from '../libs/scene3d';
import { generateConeOBJ } from '../libs/cg2.js';
import { Object3D } from '../libs/object3d';
import { Light3D } from '../libs/light3d';
import { Camera3D } from '../libs/camera3d';
//import 

// Functions and arrays for the communication with the API
import {
  agents, obstacles, trafficLights, 
  destinations, roads, initAgentsModel,
  update, getAgents, getObstacles, 
  getTrafficLights, getDestinations, getRoads
} from '../libs/api_connection.js';

// Define the shader code, using GLSL 3.00
//import vsGLSL from '../assets/shaders/vs_color.glsl?raw';
//import fsGLSL from '../assets/shaders/fs_color.glsl?raw';

import vsGLSL from '../assets/shaders/vs_phong_302.glsl?raw';
import fsGLSL from '../assets/shaders/fs_phong_302.glsl?raw';

// Chatgpt function to convert file into string
function loadText(path) {
  const xhr = new XMLHttpRequest();
  xhr.open("GET", path, false);  // false = synchronous
  xhr.send(null);
  return xhr.status >= 200 && xhr.status < 300 ? xhr.responseText : "";
}

const objTextDestination = loadText("../assets/obj/destination.obj");

const objTextAgent = loadText("../assets/obj/agentes.obj");

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
  const canvas = document.querySelector('canvas');
  gl = canvas.getContext('webgl2');
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
  let camera = new Camera3D(0,
    10,             // Distance to target
    4,              // Azimut
    0.8,              // Elevation
    [0, 0, 10],
    [0, 0, 0]);
  // These values are empyrical.
  // Maybe find a better way to determine them
  camera.panOffset = [0, 8, 0];
  scene.setCamera(camera);
  scene.camera.setupControls();

  let light = new Light3D(0, [3, 3, 5],              // Position
                             [0.3, 0.3, 0.3, 1.0],   // Ambient
                             [1.0, 1.0, 1.0, 1.0],   // Diffuse
                             [1.0, 1.0, 1.0, 1.0]);  // Specular
  scene.addLight(light);
}

function randRange(min, max) {
  return min + Math.random() * (max - min);
}

function setupObjects(scene, gl, programInfo) {
  // Create VAOs for the different shapes
  const baseCube = new Object3D(-1);
  baseCube.prepareVAO(gl, programInfo, objTextAgent);
  // Use objloader function with

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
    agent.scale = { x: 0.5, y: 0.5, z: 0.5 };
    scene.addObject(agent);
  }

  // Copy the properties of the base objects
  for (const agent of obstacles) {
    const sides = 4;
    const height = randRange(0.5, 1.5);
    const rBottom = randRange(0.3, 0.7);
    const rTop = randRange(0.3, 0.7); // same as rBottom if you want cylinder

    const objText = generateConeOBJ(sides, height, rBottom, rBottom);

    const baseCone = new Object3D(-2);
    baseCone.prepareVAO(gl, programInfo, objText);

    agent.arrays = baseCone.arrays;
    agent.bufferInfo = baseCone.bufferInfo;
    agent.vao = baseCone.vao;

    agent.color = [0.0, 0.0, 1.0, 1.0];
    scene.addObject(agent);
  }

  for (const agent of trafficLights) {
    const trafficLightObj = new Object3D(-3);
    trafficLightObj.prepareVAO(gl, programInfo);

    agent.arrays = trafficLightObj.arrays;
    agent.bufferInfo = trafficLightObj.bufferInfo;
    agent.vao = trafficLightObj.vao;
    agent.tra
    agent.scale = { x: 0.3, y: 1.0, z: 0.3 };
    agent.color = [0.0, 1.0, 0.0, 1.0];
    scene.addObject(agent);
  }

  for (const agent of destinations) {
    const destinationObj = new Object3D(-4);
    destinationObj.prepareVAO(gl, programInfo, objTextDestination);

    agent.arrays = destinationObj.arrays;
    agent.bufferInfo = destinationObj.bufferInfo;
    agent.vao = destinationObj.vao;
    agent.color = [1.0, 0.0, 0.0, 1.0];
    agent.scale = { x: 0.3, y: 1.0, z: 0.3 };
    scene.addObject(agent);
  }

  for (const agent of roads) {
    const roadObj = new Object3D(-5, [14, 0, 14]);
    roadObj.prepareVAO(gl, programInfo);

    agent.arrays = roadObj.arrays;
    agent.bufferInfo = roadObj.bufferInfo;
    agent.vao = roadObj.vao;
    agent.scale = {x: 50, y: 0.1, z: 50};
    agent.color = [0.6, 0.6, 0.6, 1];
    scene.addObject(agent);
  }

}

// Draw an object with its corresponding transformations
function drawObject(gl, programInfo, object, viewProjectionMatrix, fract) {
  // Prepare the vector for translation and scale
  let v3_tra = object.posArray;
  let v3_sca = object.scaArray;

  
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
  }
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

  for (let object of scene.objects) {
    drawObject(gl, phongProgramInfo, object, viewProjectionMatrix, fract);
  }

  // Poner arreglo pos luces
  let globalUniforms = {
        u_viewWorldPosition: scene.camera.posArray,
        u_lightWorldPosition: scene.lights[0].posArray,
        u_ambientLight: scene.lights[0].ambient,
        u_diffuseLight: scene.lights[0].diffuse,
        u_specularLight: scene.lights[0].specular,

    }

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
  const fov = 60 * Math.PI / 180;
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
