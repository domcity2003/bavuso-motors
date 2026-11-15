"""Photoreal Cycles product render of a Bavuso model in Blender.
Run (after tools/export-render-mesh.py):
  BAVUSO_MODEL=adventure ../.tools/blender-5.2.3-windows-x64/blender.exe -b -P tools/render-cycles.py -- [samples] [views]
Imports cad/render/bavuso.obj (mm, X forward / Y left / Z up), turns the material names written by the
exporter into physical materials, lights a white product studio and writes visuals/cycles-<model>-<view>.png.

What makes it read as a photo rather than a CAD screenshot:
  - a bevel shader on hard-surface materials, so sharp CAD edges catch a thin highlight like real
    (always slightly rounded) machined and moulded edges;
  - a soft studio: a large overhead softbox, a key from the front quarter, two strip lights for rim highlights
    and a bright-top / dark-floor environment so the matte-black paint shows its shape;
  - micro-texture bump on rubber, textured plastics and paint, and brushed-metal anisotropy;
  - a shadow-catcher floor composited over a near-white page, as in the baseline images.
"""
import bpy, bmesh, math, sys, os
MODEL=os.environ.get('BAVUSO_MODEL','integrated')
PREFIX='' if MODEL=='integrated' else MODEL+'-'     # visuals/cycles-adventure-side.png etc.
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAMPLES=int(argv[0]) if argv else 128
VIEWS=argv[1].split(',') if len(argv)>1 else ['side','front34','rear34']

bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
bpy.ops.wm.obj_import(filepath=str(R/'cad/render/bavuso.obj'),forward_axis='Y',up_axis='Z',global_scale=0.001)
parts=[o for o in sc.objects if o.type=='MESH']

# FreeCAD tessellates face by face, so shared edges are split: weld them, then smooth by angle so
# fillets and tyres shade smoothly while panel creases stay sharp.
for o in parts:
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=2e-5)
    bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=True
    o.data.set_sharp_from_angle(angle=math.radians(30))

def mat(name,base,rough=.5,metal=0.,coat=0.,coat_rough=.3,emit=None,strength=0.,transmit=0.,ior=1.45,spec=.5,alpha=1.,
        bevel=0.,bump=0.,bump_scale=800.,aniso=0.,sheen=0.):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True;nt=m.node_tree;b=nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*base,1);b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal;b.inputs['Coat Weight'].default_value=coat
    b.inputs['Coat Roughness'].default_value=coat_rough;b.inputs['IOR'].default_value=ior
    b.inputs['Transmission Weight'].default_value=transmit;b.inputs['Specular IOR Level'].default_value=spec;b.inputs['Alpha'].default_value=alpha
    b.inputs['Anisotropic'].default_value=aniso;b.inputs['Sheen Weight'].default_value=sheen
    if emit:b.inputs['Emission Color'].default_value=(*emit,1);b.inputs['Emission Strength'].default_value=strength
    normal=None
    if bevel:                                           # rounded-edge highlight on hard CAD edges (radius in m)
        bv=nt.nodes.new('ShaderNodeBevel');bv.inputs['Radius'].default_value=bevel;bv.samples=6;normal=bv.outputs['Normal']
    if bump:                                            # micro texture: rubber, grained plastic, paint orange-peel
        tc=nt.nodes.new('ShaderNodeTexCoord');nz=nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value=bump_scale;nz.inputs['Detail'].default_value=4
        nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
        bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=bump;bp.inputs['Distance'].default_value=.0002
        nt.links.new(nz.outputs['Fac'],bp.inputs['Height'])
        if normal is not None:nt.links.new(normal,bp.inputs['Normal'])
        normal=bp.outputs['Normal']
    if normal is not None:
        nt.links.new(normal,b.inputs['Normal'])
        if coat:nt.links.new(normal,b.inputs['Coat Normal'])
    return m
g=lambda v:(v,v,v)
MATS=dict(
    paint=mat('paint',g(.010),.5,coat=.2,coat_rough=.25,spec=.45,bevel=.004,bump=.04,bump_scale=2500),   # satin black
    paint_texture=mat('paint_texture',g(.012),.68,spec=.3,bevel=.002,bump=.25,bump_scale=1800),            # grained battery/belly plates
    dark_metal=mat('dark_metal',g(.02),.4,metal=.6,spec=.4,bevel=.0015),
    caliper=mat('caliper',g(.025),.32,metal=.7,coat=.3,bevel=.0015),
    tyre=mat('tyre',g(.014),.82,spec=.3,sheen=.1,bump=.5,bump_scale=1200),
    rubber=mat('rubber',g(.016),.8,spec=.2,bump=.3,bump_scale=600),
    belt=mat('belt',g(.02),.7,spec=.25,bump=.15,bump_scale=700),
    rider=mat('rider',(.30,.31,.33),.75,spec=.3),   # matte grey mannequin (rider-figure.py)
    seat=mat('seat',g(.014),.62,spec=.3,sheen=.3,bump=.35,bump_scale=350,bevel=.003),
    chrome=mat('chrome',g(.92),.05,metal=1),disc=mat('disc',g(.6),.3,metal=1,aniso=.6,bevel=.0008),
    alu=mat('alu',g(.75),.25,metal=1,aniso=.5,bevel=.001),
    bolt=mat('bolt',g(.05),.35,metal=.9,bevel=.0006),                      # black-oxide button heads (zinc read as white dots)
    hose=mat('hose',g(.012),.42,spec=.4,coat=.25,coat_rough=.3,bump=.08,bump_scale=3000),   # brake hose / harness sleeve
    mirror=mat('mirror',g(.95),.02,metal=1),
    reservoir=mat('reservoir',g(.03),.12,spec=.6,coat=.7,coat_rough=.05),   # smoked fluid reservoir
    gold=mat('gold',(.85,.55,.18),.28,metal=1,bevel=.0008),
    wheel=mat('wheel',g(.012),.38,metal=.2,coat=.35,coat_rough=.25,bevel=.0015),
    plastic=mat('plastic',g(.025),.48,bevel=.0015,bump=.1,bump_scale=1500),
    reflector=mat('reflector',(.9,.32,.02),.15,coat=.8,emit=(1,.4,.05),strength=.3),
    lamp_white=mat('lamp_white',g(.9),.1,emit=(1,.97,.92),strength=25),
    lamp_lens=mat('lamp_lens',g(.02),.05,spec=1.,coat=1.,coat_rough=.02),
    lamp_red=mat('lamp_red',(.6,.01,.01),.2,emit=(1,.03,.02),strength=10),
    lamp_amber=mat('lamp_amber',(.55,.2,.01),.08,spec=.8,coat=1.,coat_rough=.03,bevel=.002),   # unlit amber lens (was glowing)
    glass=mat('glass',(.55,.6,.65),.03,spec=1.,alpha=.15),   # see-through screen with reflections
    plate=mat('plate',g(.82),.4))
for o in parts:
    for s in o.material_slots:
        if s.material and s.material.name.split('.')[0] in MATS:s.material=MATS[s.material.name.split('.')[0]]

# Product-shot studio: the floor is a shadow catcher on a transparent film, and each render is laid
# over a white page afterwards, so there is no horizon line, only the bike's contact shadow.
bpy.ops.mesh.primitive_plane_add(size=40,location=(0.7,0,0))
floor=bpy.context.active_object;floor.is_shadow_catcher=True
# Environment seen in reflections: bright overhead, falling to a dark floor below the horizon, so curved
# black panels show a light-to-dark gradient instead of one flat tone.
w=bpy.data.worlds.new('studio');sc.world=w;w.use_nodes=True;nt=w.node_tree
bg=nt.nodes['Background'];bg.inputs['Strength'].default_value=.4
tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Generated'],sep.inputs[0])
ramp=nt.nodes.new('ShaderNodeValToRGB');nt.links.new(sep.outputs['Z'],ramp.inputs['Fac'])
cr=ramp.color_ramp;cr.elements[0].position=.45;cr.elements[0].color=(.05,.05,.055,1)
cr.elements[1].position=.75;cr.elements[1].color=(1,1,1,1)
nt.links.new(ramp.outputs['Color'],bg.inputs['Color'])
def area(name,loc,energy,size,target=(0.74,0,0.55),shape='DISK',size_y=None):
    l=bpy.data.lights.new(name,'AREA');l.energy=energy;l.shape=shape;l.size=size
    if size_y:l.size_y=size_y
    o=bpy.data.objects.new(name,l);sc.collection.objects.link(o);o.location=loc
    d=Vector(target)-Vector(loc);o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    return o
area('softbox_top',(0.74,0,3.6),1800,3.2,shape='RECTANGLE',size_y=1.6)
area('key',(3.4,3.6,2.6),1100,2.2)
area('fill',(-2.0,4.2,1.1),350,3.5)
area('strip_left',(-0.6,2.6,1.4),500,0.35,shape='RECTANGLE',size_y=2.4,target=(0.74,0,0.7))
area('strip_right',(2.2,-3.2,1.6),700,0.35,shape='RECTANGLE',size_y=2.4,target=(0.74,0,0.7))
area('kicker_rear',(-2.4,-1.2,0.9),400,1.5)

centre=bpy.data.objects.new('centre',None);sc.collection.objects.link(centre);centre.location=(0.74,0,0.58)
cam_d=bpy.data.cameras.new('cam');cam=bpy.data.objects.new('cam',cam_d);sc.collection.objects.link(cam);sc.camera=cam
t=cam.constraints.new('TRACK_TO');t.target=centre;t.track_axis='TRACK_NEGATIVE_Z';t.up_axis='UP_Y'
VIEW=dict(side=((0.74,7.6,0.6),85),side_right=((0.74,-7.6,0.6),85),front34=((3.9,4.3,1.15),62),rear34=((-3.0,-4.3,1.4),60),
          hero=((3.2,3.0,0.55),55),front=((5.5,0,0.95),85),detail_front=((2.15,1.15,0.55),50))
CENTRE=dict(detail_front=(1.42,0,0.42))
DOF=dict(detail_front=2.8,hero=8.0,front34=11.0)

sc.render.engine='CYCLES';cy=sc.cycles
cy.samples=SAMPLES;cy.use_denoising=True;cy.use_adaptive_sampling=True;cy.adaptive_threshold=.02
cy.max_bounces=8;cy.glossy_bounces=4;cy.transparent_max_bounces=8
prefs=bpy.context.preferences.addons['cycles'].preferences
for dev in ('OPTIX','CUDA','HIP','ONEAPI'):
    try:
        prefs.compute_device_type=dev;prefs.get_devices()
        if any(d.type==dev for d in prefs.devices):
            for d in prefs.devices:d.use=True
            cy.device='GPU';break
    except Exception:pass
print('cycles device:',cy.device,flush=True)
sc.render.resolution_x,sc.render.resolution_y=int(os.environ.get('BAVUSO_RES_X',2000)),int(os.environ.get('BAVUSO_RES_Y',1250))
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Base Contrast'
sc.view_settings.exposure=float(os.environ.get('BAVUSO_EXPOSURE','-3.0'))
sc.render.film_transparent=True;cy.film_transparent_glass=True
sc.render.image_settings.color_mode='RGBA'
import numpy as np
for v in [v for v in VIEWS if v in VIEW]:
    cam.location,cam_d.lens=VIEW[v];centre.location=CENTRE.get(v,(0.74,0,0.58))
    # Depth of field like a real lens: shallow on the close detail shot, barely there on the full-bike views.
    cam_d.dof.use_dof=v in DOF;cam_d.dof.focus_object=centre;cam_d.dof.aperture_fstop=DOF.get(v,8)
    path=str(R/f'visuals/cycles-{PREFIX}{v}.png');sc.render.filepath=path
    bpy.ops.render.render(write_still=True)
    # Lay the render over a near-white page (straight alpha; shadows come through as partial alpha).
    im=bpy.data.images.load(path);px=np.array(im.pixels[:]).reshape(-1,4)
    a=px[:,3:4];px[:,:3]=px[:,:3]*a+.955*(1-a);px[:,3]=1
    im.pixels[:]=px.ravel();im.file_format='PNG';im.save()
    print('wrote',path,flush=True)
