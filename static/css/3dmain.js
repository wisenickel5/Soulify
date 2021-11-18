import './main.css'

import* as THREE from'three';
import {OrbitControls} from'three/examples/jsm/controls/OrbitControls';
const scene =new THREE.Scene();
//field of view,aspect ration
const camera= new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight, 0.1,1000);
const ren=new THREE.WebGL1Renderer({canvas:document.querySelector("#bg"),});
ren.setPixelRatio(window.devicePixelRatio);
ren.setSize(window.innerWidth,innerHeight);
camera.position.setZ(30);
ren.render(scene,camera);
const geo=new THREE.TorusGeometry(10,3,16,100)
//object
const mat=new THREE.MeshStandardMaterial({color:0xFF6347,wireframe:true});
const tor=new THREE.Mesh(geo,mat);
scene.add(tor)
//ligthing
const point= new THREE.PointLight(0xffffff)
point.position.set(5,5,5)
const aml=new THREE.AmbientLight(0xffffff);
scene.add(point,aml)
const helper=new THREE.PointLightHelper(point)
scene.add(helper)
//controller to move around canvas
const controls = new OrbitControls(camera,ren.domElement);



//stars
function star(){
    const geom =new THREE.SphereGeometry(0.25,24,24);
    const matt=new THREE.MeshStandardMaterial({color:0xffffff})
    const sta= new THREE.Mesh(geom,matt);
    const [x,y,z] =Array(3).fill.map(()=>THREE.MathUtils.randFloatSpread(100));
    sta.position.set(x,y,z);
    scene.add(star)
}
Array(200).fill().forEach(star)
//background


//moving object
function animate(){
    requestAnimationFrame(animate);
tor.rotation.x+=0.01;
tor.rotation.y+=0.005;
tor.rotation.z+=0.01;
controls.update();
    ren.render(scene,camera);
}