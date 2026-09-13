import { useEffect, useRef } from 'react'
import * as THREE from 'three'

type NebulaBackgroundProps = {
    className?: string
    /** CSS filter tweaks, same idea as hue-rotate/saturate/brightness knobs */
    hue?: number
    saturation?: number
    brightness?: number
}

const VERTEX_SHADER = `void main(){ gl_Position = vec4(position, 1.0); }`

const FRAGMENT_SHADER = `
precision highp float;
uniform float u_time;
uniform vec2 u_resolution;
uniform vec2 u_mouse;

vec3 mod289(vec3 x){return x - floor(x*(1.0/289.0))*289.0;}
vec2 mod289(vec2 x){return x - floor(x*(1.0/289.0))*289.0;}
vec3 permute(vec3 x){return mod289(((x*34.0)+1.0)*x);}
float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187,0.366025403784439,-0.577350269189626,0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0,0.0) : vec2(0.0,1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod289(i);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
  m = m*m; m = m*m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
float fbm(vec2 p){
  float v = 0.0; float a = 0.55;
  for(int i=0;i<4;i++){ v += a*snoise(p); p *= 2.05; a *= 0.5; }
  return v;
}

void main(){
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  vec2 p = uv;
  p.x *= u_resolution.x / u_resolution.y;

  float t = u_time * 0.05;
  vec2 drift = (u_mouse - 0.5) * 0.12;

  vec2 st = p * 0.85 + drift;
  st += vec2(fbm(st + t), fbm(st - t)) * 0.35;

  vec3 col = vec3(0.005, 0.005, 0.012);

  vec2 c1 = vec2(u_resolution.x / u_resolution.y * 0.62, 0.85) + drift;
  float d1 = length(p - c1);
  float n1 = fbm(st * 1.4 + t * 2.0);
  float mass = smoothstep(1.15, 0.05, d1 + n1 * 0.32);

  float tongue = smoothstep(0.55, 0.02, abs(p.x - (u_resolution.x/u_resolution.y*0.58) - n1*0.22)) * smoothstep(1.2, 0.1, abs(uv.y - 0.55));

  vec2 c2 = vec2(u_resolution.x / u_resolution.y * 1.05, 0.5);
  float d2 = length(p - c2);
  float mass2 = smoothstep(0.9, 0.0, d2 + fbm(st*1.1 - t)*0.25);

  vec3 deepIndigo = vec3(0.05, 0.02, 0.15);
  vec3 purple = vec3(0.2, 0.1, 0.6);
  vec3 hotViolet = vec3(0.5, 0.3, 1.0);

  col = mix(col, deepIndigo, clamp(mass*0.9 + mass2*0.7, 0.0, 1.0));
  col = mix(col, purple, clamp(mass*mass*1.1 + mass2*0.55, 0.0, 1.0));
  col += hotViolet * tongue * mass * 0.85;

  float pulse = 0.92 + 0.08 * sin(u_time * 0.4);
  col *= pulse;

  float vig = smoothstep(1.6, 0.35, length(uv - vec2(0.45, 0.5)));
  col *= mix(0.55, 1.0, vig);
  col *= mix(0.35, 1.0, smoothstep(0.0, 0.55, uv.x));

  gl_FragColor = vec4(col, 1.0);
}
`

function clamp(value: number, min: number, max: number) {
    return Math.min(max, Math.max(min, value))
}

/**
 * Full-bleed animated indigo/violet nebula background, rendered with a
 * raw-Three.js fullscreen shader. Drop it in a positioned ancestor
 * (position: relative) with other content stacked above it via z-index.
 *
 * npm install three
 */
export default function NebulaBackground({
    className,
    hue = 0,
    saturation = 1,
    brightness = 1,
}: NebulaBackgroundProps) {
    const canvasRef = useRef<HTMLCanvasElement | null>(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false })
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

        const scene = new THREE.Scene()
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)

        const uniforms = {
            u_time: { value: 0 },
            u_resolution: { value: new THREE.Vector2(1, 1) },
            u_mouse: { value: new THREE.Vector2(0.5, 0.5) },
        }

        const material = new THREE.ShaderMaterial({
            uniforms,
            vertexShader: VERTEX_SHADER,
            fragmentShader: FRAGMENT_SHADER,
        })
        const geometry = new THREE.PlaneGeometry(2, 2)
        const mesh = new THREE.Mesh(geometry, material)
        scene.add(mesh)

        const mouseTarget = { x: 0.5, y: 0.5 }
        const parent = canvas.parentElement

        function resize() {
            const width = parent ? parent.clientWidth : window.innerWidth
            const height = parent ? parent.clientHeight : window.innerHeight
            renderer.setSize(width, height)
            uniforms.u_resolution.value.set(width, height)
        }

        function onPointerMove(e: PointerEvent) {
            const rect = canvas?.getBoundingClientRect()
            if (!rect) return
            mouseTarget.x = (e.clientX - rect.left) / rect.width
            mouseTarget.y = 1 - (e.clientY - rect.top) / rect.height
        }

        resize()
        window.addEventListener('resize', resize)
        window.addEventListener('pointermove', onPointerMove)

        const resizeObserver = parent ? new ResizeObserver(resize) : null
        resizeObserver?.observe(parent!)

        const clock = new THREE.Clock()
        let frameId = 0
        function animate() {
            frameId = requestAnimationFrame(animate)
            uniforms.u_time.value = clock.getElapsedTime()
            uniforms.u_mouse.value.x += (mouseTarget.x - uniforms.u_mouse.value.x) * 0.03
            uniforms.u_mouse.value.y += (mouseTarget.y - uniforms.u_mouse.value.y) * 0.03
            renderer.render(scene, camera)
        }
        animate()

        return () => {
            cancelAnimationFrame(frameId)
            window.removeEventListener('resize', resize)
            window.removeEventListener('pointermove', onPointerMove)
            resizeObserver?.disconnect()
            geometry.dispose()
            material.dispose()
            renderer.dispose()
        }
    }, [])

    const safeHue = clamp(hue, -180, 180)
    const safeSaturation = clamp(saturation, 0, 2)
    const safeBrightness = clamp(brightness, 0.35, 1.65)
    const filter =
        safeHue === 0 && safeSaturation === 1 && safeBrightness === 1
            ? undefined
            : `hue-rotate(${safeHue}deg) saturate(${safeSaturation}) brightness(${safeBrightness})`

    return (
        <canvas
            ref={canvasRef}
            className={className}
            style={{
                position: 'absolute',
                inset: 0,
                display: 'block',
                width: '100%',
                height: '100%',
                pointerEvents: 'none',
                filter,
            }}
        />
    )
}
