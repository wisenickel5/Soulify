const canvas = document.getElementById('bg'); // Be sure to change this 
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

var text = "Explore Music in a new way";
const geometry = new THREE.TextGeometry( );
const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
const cube = new THREE.Mesh( geometry, material );
scene.add( cube );

camera.position.z = 5;

const animate = function () {
    requestAnimationFrame( animate );

    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;

    renderer.render( scene, camera );
};

animate();