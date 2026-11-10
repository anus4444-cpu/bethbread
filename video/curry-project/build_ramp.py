import subprocess, glob, json, sys, os
U='/root/.claude/uploads/942da50e-8dd2-581d-8e43-76fc1bffaba5'
S=sys.argv[1]; os.makedirs(S+'/ramp',exist_ok=True)
ids={l.split()[0]:l.split()[1] for l in open(S+'/clips.txt')}
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
    f=glob.glob(f'{U}/{ids[c]}-*.mp4')[0]; parts=[]
    for k,(a,b,sp) in enumerate(pieces):
        ramp=f"fps=30,trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},"
        if sp<1 and name not in ("s12","s15"): ramp+="minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
        o=f'{S}/ramp/{name}_{k}.mp4'
        if os.environ.get('ONLY') and name not in os.environ['ONLY'].split(','):
            parts.append(o); continue
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',f,'-an','-vf',ramp+GRADE.format(cx=cx,cy=cy),'-c:v','libx264','-crf','14','-preset','medium',o],check=True)
        parts.append(o)
    lst=f'{S}/ramp/{name}.txt'; open(lst,'w').write(''.join(f"file '{p}'\n" for p in parts))
    so=f'{S}/ramp/{name}.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',so],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',so]))
    out.append({'name':name,'start':round(t,3),'dur':round(d,3)}); t+=d; segfiles.append(so)
open(S+'/segs_ramp.json','w').write(json.dumps(out))
open(S+'/ramp/all.txt','w').write(''.join(f"file '{p}'\n" for p in segfiles))
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',S+'/ramp/all.txt','-c','copy',S+'/base_ramp.mp4'],check=True)
print('total',round(t,2)); print(json.dumps(out))
