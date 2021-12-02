import * as THREE from 'https://cdn.skypack.dev/three@0.135.0';
import { TextGeometry } from "./TextGeometry.js";

const canvas = document.getElementById('canvas'); // Be sure to change this 
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 
    30, // Field of View
    5, // Aspect Ratio
    0.1, // Near Clipping Plane
    100 // Far Clipping Plane
);

const renderer = new THREE.WebGLRenderer( {antialias: true} );
canvas.appendChild( renderer.domElement );
renderer.setSize( canvas.clientWidth, canvas.clientHeight );

window.addEventListener( 'resize', onWindowResize, false );	
function onWindowResize() {
   camera.aspect = 5;
   camera.updateProjectionMatrix();
   renderer.setSize( canvas.clientWidth, canvas.clientHeight );
};

var textString = "Explore Music in a new way";

var textMaterial = new THREE.MeshPhongMaterial( 
    { color: 0xff0000, specular: 0xffffff }
  );

const geometry = new TextGeometry( textString, {
    font: "Gotham_Medium_Regular",
    size: 80,
    height: 5,
    curveSegments: 12,
    bevelEnabled: true,
    bevelThickness: 10,
    bevelSize: 8,
    bevelOffset: 0,
    bevelSegments: 5
});

const text = new THREE.Mesh( geometry, textMaterial );
scene.add( text );

camera.position.z = 5;

const animate = function () {
    requestAnimationFrame( animate );

    text.rotation.x += 0.01;
    text.rotation.y += 0.01;

    renderer.render( scene, camera );
};

animate();