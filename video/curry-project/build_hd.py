import subprocess, glob, json, sys, os
U='/root/.claude/uploads/942da50e-8dd2-581d-8e43-76fc1bffaba5'
S=sys.argv[1]; os.makedirs(S+'/hd',exist_ok=True)
ids={l.split()[0]:l.split()[1] for l in open(S+'/clips.txt')}
OM=json.load(open(S+'/../origmap.json'))
ORIG={'c1':'IMG_7045.MOV','c2':'IMG_7046.MOV','c3':'IMG_7047.MOV','c4':'IMG_7048.MOV','c7':'IMG_7050.MOV','c8':'IMG_7052.MOV','c9':'IMG_7053.MOV','c10':'IMG_7054.MOV','c12':'IMG_7057.MOV','c13':'IMG_7058.MOV','c14':'IMG_7059.MOV','c15':'IMG_7060.MOV','c16':'IMG_7061.MOV'}
for extra in ('IMG_7049.MOV','IMG_7056.MOV'):
    pass
if os.path.exists(S+'/../orig/IMG_7049.MOV'): ORIG['c5']='IMG_7049.MOV'
if os.path.exists(S+'/../orig/IMG_7056.MOV'): ORIG['c11']='IMG_7056.MOV'
TM="zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
def meta(f):
    o=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=color_transfer,r_frame_rate','-of','json',f]))['streams'][0]
    return o.get('color_transfer')=='arib-std-b67', o['r_frame_rate']=='240/1'
# name, clip, cx, cy, pieces [(in,out,speed)] ; speed<1 = slow-mo (interpolated)
SEG=[
 ('h1','16',.55,.62,[(2.6,4.06,0.73)]),
 ('h2','15',.50,.57,[(0.2,1.4,1.0)]),
 ('s1','1',.46,.455,[(1.2,3.0,0.8)]),                 # oil pour slow
 ('s2','2',.55,.45,[(0.5,2.2,2.5),(2.2,3.6,0.75)]),   # onions drop slow
 ('s3','3',.49,.50,[(1.0,5.0,3.0)]),
 ('s4','4',.50,.50,[(0.0,12.0,8.0)]),
 ('s5','5',.50,.50,[(0.0,0.6,2.0),(0.6,1.9,0.65)]),   # chillies slow
 ('s6','7',.48,.40,[(0.0,9.0,6.4)]),
 ('s7','8',.55,.38,[(0.0,0.4,2.0),(0.4,2.4,0.8)]),    # tomatoes slow
 ('s8','9',.52,.41,[(0.0,3.0,2.5)]),
 ('s9','10',.50,.43,[(1.5,2.6,3.0),(2.6,4.0,0.7)]),   # chilli powder slow
 ('s10','11',.55,.44,[(3.0,3.8,2.0),(3.8,5.8,0.8)]),  # curd slow
 ('s11','12',.58,.43,[(0.0,6.0,3.75)]),
 ('s12','13',.50,.50,[(2.0,8.0,6.0),(8.0,9.5,0.75)]), # chicken slow
 ('s13','14',.50,.43,[(0.0,2.9,2.0)]),
 ('s14','15',.50,.57,[(0.0,0.5,1.5),(0.5,2.0,0.65),(2.0,3.0,1.0)]),  # lid lift slow
 ('s15','16',.55,.62,[(0.0,2.6,0.75)]),               # coriander slow
]
GRADE=("hqdn3d=2:1.5:4:4,crop=w='trunc(iw/1.08/2)*2':h='trunc(iw/1.08*16/9/2)*2':x='max(0,min(iw-ow,iw*{cx}-ow/2))':y='max(0,min(ih-oh,ih*{cy}-oh/2))',"
       "scale=1080:1920:flags=lanczos,colorbalance=rs=0.03:bs=-0.03:rm=0.03:bm=-0.02,curves=master='0/0 0.1/0.05 0.5/0.52 0.92/0.96 1/1',"
       "vibrance=intensity=0.25,eq=saturation=1.08:gamma=1.03,cas=strength=0.6,vignette=angle=PI/4.5:mode=forward,fps=30,format=yuv420p")
out=[]; t=0; segfiles=[]
for name,c,cx,cy,pieces in SEG:
    key='c'+c; isorig=key in ORIG
    f=S+'/../orig/'+ORIG[key] if isorig else glob.glob(f'{U}/{ids[c]}-*.mp4')[0]
    hdr,hfr=meta(f) if isorig else (False,False); parts=[]
    for k,(a,b,sp) in enumerate(pieces):
        if hfr: ramp=f"trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps=30,"
        else:
            ramp=f"fps=30,trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},"
            if sp<1 and name not in ("s12","s15"): ramp+="minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
        if hdr: ramp+=TM
        o=f'{S}/hd/{name}_{k}.mp4'
        if os.environ.get('ONLY') and name not in os.environ['ONLY'].split(','):
            parts.append(o); continue
        print(name,k,'orig' if isorig else 'WA','hdr' if hdr else '','240fps' if hfr else '',flush=True)
        g=GRADE.format(cx=cx,cy=cy)
        if isorig: g=g.replace('hqdn3d=2:1.5:4:4,','').replace('vibrance=intensity=0.25','vibrance=intensity=0.12').replace('cas=strength=0.6','cas=strength=0.35')
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',f,'-an','-vf',ramp+g,'-c:v','libx264','-crf','14','-preset','medium',o],check=True)
        parts.append(o)
    lst=f'{S}/hd/{name}.txt'; open(lst,'w').write(''.join(f"file '{p}'\n" for p in parts))
    so=f'{S}/hd/{name}.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',so],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',so]))
    out.append({'name':name,'start':round(t,3),'dur':round(d,3)}); t+=d; segfiles.append(so)
open(S+'/segs_hd.json','w').write(json.dumps(out))
open(S+'/hd/all.txt','w').write(''.join(f"file '{p}'\n" for p in segfiles))
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',S+'/hd/all.txt','-c','copy',S+'/base_hd.mp4'],check=True)
print('total',round(t,2)); print(json.dumps(out))
