import subprocess, glob, json, sys
U='/root/.claude/uploads/942da50e-8dd2-581d-8e43-76fc1bffaba5'
S=sys.argv[1]
ids={l.split()[0]:l.split()[1] for l in open(S+'/clips.txt')}
# name, clip, in, out, speed, cx, cy, side(frac of width)
SEG=[
 ('h1','16',2.6,4.06,0.73,.55,.62,.92),
 ('h2','15',0.2,1.4,1.0,.50,.57,.92),
 ('s1','1',1.0,3.4,2.0,.46,.455,.90),
 ('s2','2',0.5,4.5,2.0,.55,.45,.90),
 ('s3','3',1.0,5.0,3.0,.49,.50,.90),
 ('s4','4',0.0,12.0,6.0,.50,.50,.90),
 ('s5','5',0.0,2.5,1.5,.50,.50,.90),
 ('s6','7',0.0,9.0,5.0,.48,.40,.90),
 ('s7','8',0.0,3.5,1.75,.55,.38,.90),
 ('s8','9',0.0,3.0,2.0,.52,.41,.90),
 ('s9','10',1.5,10.5,4.5,.50,.43,.92),
 ('s10','11',3.0,7.7,2.35,.55,.44,.92),
 ('s11','12',0.0,6.0,3.0,.58,.43,.92),
 ('s12','13',2.0,11.8,4.0,.50,.50,.92),
 ('s13','14',0.0,2.9,2.0,.50,.43,.92),
 ('s14','15',0.0,3.8,1.3,.50,.57,.92),
 ('s15','16',0.0,4.06,1.3,.55,.62,.92),
]
out=[]; t=0
for name,c,a,b,sp,cx,cy,sd in SEG:
    f=glob.glob(f'{U}/{ids[c]}-*.mp4')[0]
    vf=(f"trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},"
        f"crop=w='trunc(iw/1.6/2)*2':h='trunc(iw/1.6*16/9/2)*2':x='max(0,min(iw-ow,iw*{cx}-ow/2))':y='max(0,min(ih-oh,ih*{cy}-oh/2))',"
        "scale=1080:1920:flags=lanczos,unsharp=5:5:0.8,"
        "eq=saturation=1.25:contrast=1.07:brightness=0.015,colorbalance=rm=0.05:gm=0.0:bm=-0.04:rh=0.03:bh=-0.03,fps=30,format=yuv420p")
    o=f'{S}/full_{name}.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',f,'-an','-vf',vf,'-c:v','libx264','-crf','16','-preset','medium',o],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',o]))
    out.append({'name':name,'clip':c,'start':round(t,3),'dur':round(d,3)}); t+=d
open(S+'/segs_full.json','w').write(json.dumps(out,indent=0))
open(S+'/concat_full.txt','w').write(''.join(f"file 'full_{s['name']}.mp4'\n" for s in out))
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',S+'/concat_full.txt','-c','copy',S+'/base_full.mp4'],check=True)
print('total',round(t,2)); [print(s) for s in out]
